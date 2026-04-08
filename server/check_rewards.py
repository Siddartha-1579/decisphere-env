import requests

URL = "http://127.0.0.1:7860"

# Reset env
requests.get(f"{URL}/reset")

# Take 50 steps
for i in range(50):
    res = requests.get(f"{URL}/step/{i % 5}")  # test 5 actions cyclically
    data = res.json()
    reward = data["reward_history"][-1]["reward"]
    print(f"Step {i+1} reward: {reward}")
    if not 0 < reward < 1:
        print(f"⚠️ Reward out of range at step {i+1}: {reward}")
        break
else:
    print("✅ All rewards are strictly between 0 and 1!")