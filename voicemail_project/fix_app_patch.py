from pathlib import Path

p = Path('app.py')
text = p.read_text(encoding='utf-8')
old = (
    '    requests.post("http://127.0.0.1:5000/recording", data=data)\n\n'
    '    return "Test triggered"\n\n'
    '# ==============================\n'
    '# 🚀 RUN SERVER\n'
    'if __name__ == "__main__":\n'
    '    app.run(debug=True)\n'
)
new = (
    '    requests.post("http://127.0.0.1:5000/recording", data=data)\n\n'
    '    return "Test triggered"\n\n'
    '# ==============================\n'
    '# 🧾 FETCH VOICEMAILS\n'
    '@app.route("/voicemails")\n'
    'def voicemails():\n'
    '    response = supabase.table("voicemails").select("*").execute()\n'
    '    print("🗄️ Fetch voicemails response:", response)\n'
    '    if getattr(response, "error", None):\n'
