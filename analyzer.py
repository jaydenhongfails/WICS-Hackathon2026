import base64
import json
import re

import cv2
import mediapipe as mp
import numpy as np
import ollama

from poses import get_reference_image

MODEL = "llava:13b"

mp_pose = mp.solutions.pose

# Joints used for comparison — covers all major body segments
JOINT_INDICES = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]

SYSTEM_PROMPT = """You are a yoga instructor giving feedback on a student's pose.
You will be given two images: a reference image showing ideal form, and the student's webcam image.
The student has already been given a numerical accuracy score based on exact body keypoint geometry.
Your job is only to provide qualitative feedback based on what you see.
Respond ONLY with valid JSON — no markdown, no preamble.

JSON schema:
{
  "what_good": ["<observation>", "<observation>"],
  "improve":   ["<correction>", "<correction>", "<correction>"],
  "tips":      ["<tip>", "<tip>"]
}

Be specific and reference exact body parts."""


# Extracts normalised (x, y) keypoint coordinates from an image file using MediaPipe
def _extract_keypoints(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
        results = pose.process(rgb)
    if not results.pose_landmarks:
        return None
    lm = results.pose_landmarks.landmark
    return np.array([[lm[i].x, lm[i].y] for i in JOINT_INDICES], dtype=np.float32)


# Computes joint-angle similarity between two sets of keypoints and returns a 0-100 score
def _compute_score(ref_kp, live_kp):
    # Normalise both skeletons to the same scale using hip-shoulder distance
    def normalise(kp):
        hip_mid = (kp[6] + kp[7]) / 2
        shoulder_mid = (kp[0] + kp[1]) / 2
        scale = np.linalg.norm(shoulder_mid - hip_mid) + 1e-6
        return (kp - hip_mid) / scale

    ref_norm  = normalise(ref_kp)
    live_norm = normalise(live_kp)

    # Mean per-joint distance after normalisation — lower is better
    distances = np.linalg.norm(ref_norm - live_norm, axis=1)
    mean_dist = float(np.mean(distances))

    # Map distance to 0-100: distance of 0 = 100, distance of 1.0+ = 0
    score = max(0, min(100, int((1.0 - mean_dist / 1.65) * 100)))
    return score


# Reads an image file from disk and returns it as a base64-encoded string
def _load_image_b64(path):
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


# Sends both images to the local Ollama model and returns qualitative feedback text only
def _get_feedback(pose, ref_path, image_path):
    images = []
    if ref_path:
        images.append(_load_image_b64(ref_path))
    images.append(_load_image_b64(image_path))

    cues = "\n".join(f"  {i+1}. {c}" for i, c in enumerate(pose["cues"]))
    prompt = (
        f"Pose: {pose['name']} ({pose['sanskrit']})\n"
        f"Alignment cues:\n{cues}\n\n"
        "Reference image is first, student image is second. Give feedback as JSON."
    )

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt, "images": images},
        ],
    )

    raw = response["message"]["content"]
    raw = re.sub(r"```(?:json)?|```", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "what_good": ["Pose attempted"],
            "improve":   ["Could not parse detailed feedback — try retaking the photo"],
            "tips":      ["Make sure your full body is visible in the frame"],
        }


# Extracts keypoints from both images, computes a geometric accuracy score, then fetches qualitative feedback
def analyze_pose(pose, image_path):
    ref_path = get_reference_image(pose["pose_id"])

    # Save webcam frame to a temp path readable by MediaPipe
    live_kp = _extract_keypoints(image_path)

    if live_kp is None:
        raise RuntimeError("No body detected — step back so your full body fits in the frame, then try again.")

    # Extract keypoints from the reference image and compute geometric score
    score = 50  # fallback if reference image keypoints cannot be extracted
    if ref_path:
        ref_kp = _extract_keypoints(ref_path)
        if ref_kp is not None:
            score = _compute_score(ref_kp, live_kp)

    if score >= 85:
        grade = "Excellent"
    elif score >= 70:
        grade = "Good"
    elif score >= 50:
        grade = "Fair"
    else:
        grade = "Keep Practicing"

    feedback = _get_feedback(pose, ref_path, image_path)

    return {
        "accuracy": score,
        "grade":    grade,
        **feedback,
    }