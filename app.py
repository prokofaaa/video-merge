from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, whisper

app = Flask(__name__)
model = whisper.load_model("base")

def dl(url, dst):
    r = requests.get(url, stream=True)
    with open(dst, "wb") as f:
        for c in r.iter_content(8192):
            f.write(c)
@app.route("/health")
def health():
    return "ok", 200

@app.route("/merge", methods=["POST"])
def merge():
    d = request.json
    seg = int(d.get("chunk_sec", 120))
    work = tempfile.mkdtemp()

    v = os.path.join(work, "v.mp4")
    a = os.path.join(work, "a.mp3")
    dl(d["video_url"], v); dl(d["audio_url"], a)

    merged = os.path.join(work, "merged.mp4")
    subprocess.check_call(["ffmpeg","-y","-i",v,"-i",a,"-c:v","copy","-c:a","aac",merged])

    srt = os.path.join(work, "subs.srt")
    with open(srt, "w", encoding="utf-8") as f:
        f.write(model.transcribe(a)["srt"])

    out_pat = os.path.join(work, "out_%03d.mp4")
    subprocess.check_call(["ffmpeg","-y","-i",merged,"-vf",f"subtitles={srt}",
                           "-c:v","libx264","-map","0","-segment_time", str(seg),
                           "-f","segment", out_pat])

    host = request.host_url.rstrip("/")
    parts = []
    for f in sorted(x for x in os.listdir(work) if x.startswith("out_")):
        dst = os.path.join("/opt/render/project/src", f)
        os.rename(os.path.join(work, f), dst)
        parts.append(f"{host}/{f}")

    return jsonify({"parts": parts})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
