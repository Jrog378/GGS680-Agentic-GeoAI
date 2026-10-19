"""Gemma 4 object detection via Ollama, following the Gemma docs pattern
(ai.google.dev/gemma/docs/capabilities/vision/image): prompt "detect X, output only ```json",
reply = [{"box_2d": [ymin, xmin, ymax, xmax], "label": ...}] on a 1000x1000 grid."""
import base64, json, os, re, sys, time, urllib.request
from PIL import Image, ImageDraw

MODEL = "gemma4:12b"
HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE = sys.argv[1] if len(sys.argv) > 1 else "post_2022-09-30.png"
TARGETS = sys.argv[2] if len(sys.argv) > 2 else "destroyed building"

path = os.path.join(HERE, IMAGE)
body = {
    "model": MODEL,
    "messages": [{"role": "user", "content": f"detect {TARGETS}, output only ```json",
                  "images": [base64.b64encode(open(path, "rb").read()).decode()]}],
    "think": False, "stream": False, "options": {"num_ctx": 4096, "temperature": 0},
}
t0 = time.time()
req = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json"})
out = json.load(urllib.request.urlopen(req, timeout=900))
text = out["message"]["content"]
print(f"{time.time() - t0:.1f}s, prompt tokens {out.get('prompt_eval_count')}, output tokens {out.get('eval_count')}")

m = re.search(r"```json\s+(.*?)\s+```", text, re.DOTALL)        # same extraction as the Gemma docs
dets = json.loads(m.group(1) if m else text)
print(f"{len(dets)} detections; first few: {dets[:3]}")

img = Image.open(path).convert("RGB")
W, H = img.size
draw = ImageDraw.Draw(img)
for d in dets:
    y1, x1, y2, x2 = [c / 1000 for c in d["box_2d"]]               # 0-1000 grid -> fraction
    draw.rectangle([x1 * W, y1 * H, x2 * W, y2 * H], outline=(255, 40, 40), width=4)
    draw.text((x1 * W + 4, y1 * H + 2), d.get("label", ""), fill=(255, 255, 0))
tag = TARGETS.replace(" ", "_").replace(",", "")
img.save(os.path.join(HERE, f"detect_{tag}.png"))
json.dump({"prompt": body["messages"][0]["content"], "raw": text, "detections": dets},
          open(os.path.join(HERE, f"detect_{tag}.json"), "w"), indent=2)
print("saved", f"detect_{tag}.png")
