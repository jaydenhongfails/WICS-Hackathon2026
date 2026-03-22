import os

# Path to the unzipped Kaggle dataset — update this to match your local directory
DATASET_DIR = "/Users/jaydenhong/Downloads/DATASET/TRAIN"

POSES = {
    "0": {"id": "downdog",  "name": "Downward Dog", "sanskrit": "Adho Mukha Svanasana", "pose_id": "downdog",
          "cues": [
              "Hands shoulder-width apart, fingers spread wide",
              "Feet hip-width apart, heels pressing toward the floor",
              "Hips high, forming an inverted V shape",
              "Spine long and straight, not rounded in the upper back",
              "Head between the arms, gaze toward navel or feet",
              "Arms straight, shoulder blades moving apart",
          ]},
    "1": {"id": "goddess",  "name": "Goddess Pose",  "sanskrit": "Utkata Konasana", "pose_id": "goddess",
          "cues": [
              "Feet wide apart, toes turned out at 45 degrees",
              "Knees bent deeply, tracking over the toes",
              "Hips level, tailbone dropping straight down",
              "Torso upright, core engaged",
              "Arms out at shoulder height, elbows bent at 90 degrees",
              "Gaze forward, chin parallel to the floor",
          ]},
    "2": {"id": "plank",    "name": "Plank Pose",    "sanskrit": "Phalakasana", "pose_id": "plank",
          "cues": [
              "Hands directly under shoulders, fingers spread",
              "Body in one straight line from head to heels",
              "Core and glutes firmly engaged",
              "Hips not sagging or piking upward",
              "Neck neutral, gaze slightly forward of the hands",
              "Shoulders away from the ears",
          ]},
    "3": {"id": "tree",     "name": "Tree Pose",     "sanskrit": "Vrksasana", "pose_id": "tree",
          "cues": [
              "Standing leg straight but not locked at the knee",
              "Raised foot pressed to inner thigh or calf, never the knee joint",
              "Hips level and square to the front",
              "Hands in prayer at heart center or raised overhead",
              "Core engaged for balance, gaze fixed on a still point",
          ]},
    "4": {"id": "warrior2", "name": "Warrior II",    "sanskrit": "Virabhadrasana II", "pose_id": "warrior2",
          "cues": [
              "Front knee tracking over second toe, bent at 90 degrees",
              "Back foot parallel to the short edge of the mat",
              "Hips open to the side, not squared forward",
              "Arms extended in a T-shape at shoulder height",
              "Torso directly over the pelvis, not leaning",
              "Gaze over the front middle finger",
          ]},
}


# Scans the pose's class folder in the dataset and returns the path to the first valid image found
def get_reference_image(pose_id):
    folder = os.path.join(DATASET_DIR, pose_id)
    if not os.path.isdir(folder):
        return None
    for fname in sorted(os.listdir(folder)):
        if fname.lower().endswith((".jpg", ".jpeg", ".png")):
            return os.path.join(folder, fname)
    return None


# Prints all available poses as a numbered table to stdout
def list_poses():
    print("\n" + "─" * 48)
    print(f"  {'#':<4} {'Pose':<20} {'Sanskrit'}")
    print("─" * 48)
    for key, pose in POSES.items():
        print(f"  {key:<4} {pose['name']:<20} {pose['sanskrit']}")
    print("─" * 48)


# Returns the pose dict for a given menu key, or None if the key is invalid
def get_pose(key):
    return POSES.get(key)