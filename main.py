import os
import sys
import tempfile
import textwrap
import time

import cv2

from analyzer import analyze_pose
from poses import get_pose, list_poses

WINDOW_NAME = "Yoga Analyzer  |  SPACE = capture   Q = quit"
COUNTDOWN_SECONDS = 3


# Clears the terminal screen
def clear():
    os.system("cls" if os.name == "nt" else "clear")


# Prints the app header to stdout
def header():
    print("\033[1;36m")
    print("┌─────────────────────────────────────────┐")
    print("│                 Growga                  │")
    print("└─────────────────────────────────────────┘")
    print("\033[0m")


# Opens the webcam at the given device index and sets a preferred resolution
def open_camera(index=0):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"\033[1;31m✗ Could not open camera {index}.\033[0m")
        sys.exit(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cap


# Draws corner alignment brackets and a hint bar onto the frame in-place
def draw_overlay(frame, countdown=None, message=""):
    h, w = frame.shape[:2]
    size, thick = 40, 3
    cx, cy = w // 2, h // 2
    half_w, half_h = w // 4, h // 3
    colour = (100, 220, 100)

    for x, y in [(cx - half_w, cy - half_h), (cx + half_w, cy - half_h),
                 (cx - half_w, cy + half_h), (cx + half_w, cy + half_h)]:
        dx = size if x < cx else -size
        dy = size if y < cy else -size
        cv2.line(frame, (x, y), (x + dx, y), colour, thick)
        cv2.line(frame, (x, y), (x, y + dy), colour, thick)

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - 44), (w, h), (0, 0, 0), -1)
    frame[:] = cv2.addWeighted(overlay, 0.55, frame, 0.45, 0)

    hint = message or "SPACE = capture pose    Q = quit"
    cv2.putText(frame, hint, (16, h - 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1, cv2.LINE_AA)

    if countdown:
        (tw, th), _ = cv2.getTextSize(str(countdown), cv2.FONT_HERSHEY_SIMPLEX, 5, 8)
        cv2.putText(frame, str(countdown), (cx - tw // 2, cy + th // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 8, cv2.LINE_AA)


# Shows a live countdown on screen for COUNTDOWN_SECONDS before returning
def run_countdown(cap):
    start = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        remaining = max(0, COUNTDOWN_SECONDS - int(time.time() - start))
        draw_overlay(frame, countdown=remaining, message="Hold your pose…")
        cv2.imshow(WINDOW_NAME, frame)
        cv2.waitKey(1)
        if time.time() - start >= COUNTDOWN_SECONDS:
            break


# Runs the countdown, grabs a frame, saves it as a temp JPEG, and returns the file path
def capture_frame(cap):
    run_countdown(cap)
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Failed to read frame from camera.")
    frame = cv2.flip(frame, 1)
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    cv2.imwrite(tmp.name, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return tmp.name


# Prints the analysis result with a colour-coded score bar and three feedback sections
def print_result(result, pose_name):
    accuracy = max(0, min(100, int(result.get("accuracy", 0))))
    grade = result.get("grade", "—")

    if accuracy >= 85:
        colour = "\033[1;32m"
    elif accuracy >= 70:
        colour = "\033[1;33m"
    elif accuracy >= 50:
        colour = "\033[1;35m"
    else:
        colour = "\033[1;31m"
    reset = "\033[0m"

    bar = "█" * (accuracy // 2) + "░" * (50 - accuracy // 2)

    print(f"\n  Pose: {pose_name}")
    print("─" * 55)
    print(f"  Accuracy  {colour}{accuracy:>3}%  {grade}{reset}")
    print(f"  [{bar}]")
    print("─" * 55)

    for title, items, c in [
        ("✓  What's looking good", result.get("what_good", []), "\033[32m"),
        ("↗  Areas to improve",    result.get("improve", []),   "\033[33m"),
        ("★  Practice tips",       result.get("tips", []),      "\033[36m"),
    ]:
        if items:
            print(f"\n{c}{title}{reset}")
            for item in items:
                print(f"    •  {textwrap.fill(item, width=70, subsequent_indent='       ')}")

    print("─" * 55)


# Prompts the user to pick a pose from the library and returns the selected pose dict
def choose_pose():
    clear()
    header()
    list_poses()
    print()
    while True:
        pose = get_pose(input("  Enter pose number (0–4): ").strip())
        if pose:
            return pose
        print("  ✗ Invalid selection, try again.")


# Main loop: opens webcam, waits for spacebar, captures pose, sends to Claude, prints feedback
def main():
    camera_index = 0
    if "--camera" in sys.argv:
        try:
            camera_index = int(sys.argv[sys.argv.index("--camera") + 1])
        except (IndexError, ValueError):
            pass

    pose = choose_pose()

    clear()
    header()
    print(f"  Selected: \033[1m{pose['name']}\033[0m  ({pose['sanskrit']})\n")
    print("  Alignment cues:")
    for cue in pose["cues"]:
        print(f"    •  {cue}")
    print("\n  \033[33mPress SPACE to start countdown, Q to quit.\033[0m\n")

    cap = open_camera(camera_index)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            draw_overlay(frame)
            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print("\n  Goodbye! 🙏\n")
                break

            elif key == ord(" "):
                image_path = capture_frame(cap)

                ret2, frozen = cap.read()
                if ret2:
                    frozen = cv2.flip(frozen, 1)
                    draw_overlay(frozen, message="Coach is thinking…  please wait")
                    cv2.imshow(WINDOW_NAME, frozen)
                    cv2.waitKey(1)

                print("  Analyzing pose...")
                try:
                    result = analyze_pose(pose, image_path)
                    clear()
                    header()
                    print_result(result, pose["name"])
                except RuntimeError as exc:
                    print(f"\n  \033[1;31m✗ Analysis error:\033[0m {exc}\n")
                finally:
                    os.unlink(image_path)

                again = input("\n  Again? (y = same pose / n = new pose / q = quit): ").strip().lower()
                if again == "q":
                    break
                elif again == "n":
                    cap.release()
                    cv2.destroyAllWindows()
                    pose = choose_pose()
                    cap = open_camera(camera_index)
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()