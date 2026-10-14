import os
from xml.sax.saxutils import escape

import plivo
from dotenv import load_dotenv
from flask import Flask, Response, render_template, request

import ivr_texts as t

load_dotenv()

PLIVO_AUTH_ID = os.getenv("PLIVO_AUTH_ID", "")
PLIVO_AUTH_TOKEN = os.getenv("PLIVO_AUTH_TOKEN", "")
PLIVO_FROM_NUMBER = os.getenv("PLIVO_FROM_NUMBER", "")
TARGET_NUMBER = os.getenv("TARGET_NUMBER", "")
ASSOCIATE_NUMBER = os.getenv("ASSOCIATE_NUMBER", "")
OTP_CODE = "2108"
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
AUDIO_URL = os.getenv("AUDIO_URL", "https://s3.amazonaws.com/plivocloud/Trumpet.mp3")
PORT = int(os.getenv("PORT", "5050"))

app = Flask(__name__)


def url(path):
    base = BASE_URL or request.url_root.rstrip("/")
    return escape(f"{base}{path}")


def speak(text, lang="en"):
    v = t.VOICES[lang]
    return f'<Speak voice="{v["voice"]}" language="{v["language"]}">{escape(text)}</Speak>'


def get_input(action_path, inner, num_digits=1):
    return (
        f'<GetInput action="{url(action_path)}" method="POST" inputType="dtmf" '
        f'numDigits="{num_digits}" digitEndTimeout="5" executionTimeout="15" '
        f'redirect="true">{inner}</GetInput>'
    )


def redirect(path):
    return f'<Redirect method="POST">{url(path)}</Redirect>'


def xml_response(*elements):
    body = '<?xml version="1.0" encoding="UTF-8"?><Response>' + "".join(elements) + "</Response>"
    return Response(body, mimetype="application/xml")


def get_lang():
    lang = request.values.get("lang", "en")
    return lang if lang in t.TEXTS else "en"


def place_call(to_number):
    missing = [name for name, val in [
        ("PLIVO_AUTH_ID", PLIVO_AUTH_ID),
        ("PLIVO_AUTH_TOKEN", PLIVO_AUTH_TOKEN),
        ("PLIVO_FROM_NUMBER", PLIVO_FROM_NUMBER),
        ("BASE_URL", BASE_URL),
    ] if not val]
    if missing:
        raise RuntimeError(f"Missing config in .env: {', '.join(missing)}")
    if not to_number:
        raise RuntimeError("No target phone number provided.")

    client = plivo.RestClient(PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN)
    resp = client.calls.create(
        from_=PLIVO_FROM_NUMBER,
        to_=to_number,
        answer_url=f"{BASE_URL}/answer",
        answer_method="POST",
    )
    return resp.request_uuid


@app.route("/")
def index():
    return render_template("index.html", default_number=TARGET_NUMBER)


@app.route("/make-call", methods=["POST"])
def make_call():
    to_number = (request.form.get("to") or TARGET_NUMBER).strip()
    try:
        uuid = place_call(to_number)
        msg, ok = f"Call initiated to {to_number}. Request UUID: {uuid}", True
    except Exception as e:
        msg, ok = f"Failed to place call: {e}", False
    return render_template("index.html", default_number=to_number, message=msg, ok=ok)


@app.route("/answer", methods=["GET", "POST"])
def answer():
    return xml_response(
        get_input("/verify-otp", speak(t.OTP_PROMPT), num_digits=4),
        speak(t.OTP_NO_INPUT),
        redirect("/answer"),
    )


@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    digits = request.values.get("Digits", "").strip()
    app.logger.info("OTP entered: %s", digits)
    if digits == OTP_CODE:
        return xml_response(speak(t.OTP_SUCCESS), redirect("/language-menu"))
    return xml_response(speak(t.OTP_INVALID), redirect("/answer"))


@app.route("/language-menu", methods=["GET", "POST"])
def language_menu():
    prompt = speak(t.LANGUAGE_PROMPT_EN, "en") + speak(t.LANGUAGE_PROMPT_ES, "es")
    return xml_response(
        get_input("/language-select", prompt),
        redirect("/language-menu"),
    )


@app.route("/language-select", methods=["GET", "POST"])
def language_select():
    digits = request.values.get("Digits", "").strip()
    app.logger.info("Language selection: %s", digits)
    if digits == "1":
        return xml_response(redirect("/action-menu?lang=en"))
    if digits == "2":
        return xml_response(redirect("/action-menu?lang=es"))
    return xml_response(speak(t.LANGUAGE_INVALID), redirect("/language-menu"))


@app.route("/action-menu", methods=["GET", "POST"])
def action_menu():
    lang = get_lang()
    return xml_response(
        get_input(f"/action-select?lang={lang}", speak(t.TEXTS[lang]["action_prompt"], lang)),
        redirect(f"/action-menu?lang={lang}"),
    )


@app.route("/action-select", methods=["GET", "POST"])
def action_select():
    lang = get_lang()
    texts = t.TEXTS[lang]
    digits = request.values.get("Digits", "").strip()
    app.logger.info("Action selection (%s): %s", lang, digits)

    if digits == "1":
        return xml_response(
            speak(texts["playing"], lang),
            f"<Play>{escape(AUDIO_URL)}</Play>",
            speak(texts["after_audio"], lang),
            redirect(f"/action-menu?lang={lang}"),
        )
    if digits == "2":
        if not ASSOCIATE_NUMBER:
            return xml_response(speak(texts["dial_failed"], lang), "<Hangup/>")
        return xml_response(
            speak(texts["connecting"], lang),
            f'<Dial callerId="{escape(PLIVO_FROM_NUMBER)}" timeout="30">'
            f"<Number>{escape(ASSOCIATE_NUMBER)}</Number></Dial>",
        )
    return xml_response(speak(texts["invalid"], lang), redirect(f"/action-menu?lang={lang}"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
