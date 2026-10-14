VOICES = {
    "en": {"voice": "WOMAN", "language": "en-US"},
    "es": {"voice": "WOMAN", "language": "es-ES"},
}

OTP_PROMPT = (
    "Welcome to InspireWorks. "
    "Please enter your 4 digit one time password using your keypad."
)
OTP_INVALID = "The password you entered is incorrect. Please try again."
OTP_NO_INPUT = "We did not receive any input."
OTP_SUCCESS = "Thank you. You have been successfully authenticated."

LANGUAGE_PROMPT_EN = "For English, press 1."
LANGUAGE_PROMPT_ES = "Para español, presione 2."
LANGUAGE_INVALID = "Invalid selection."

TEXTS = {
    "en": {
        "action_prompt": (
            "To listen to a short audio message, press 1. "
            "To speak with a live associate, press 2."
        ),
        "invalid": "Invalid selection. Please try again.",
        "playing": "Playing your audio message now.",
        "after_audio": "Returning to the menu.",
        "connecting": "Please hold while we connect you to a live associate.",
        "dial_failed": "We could not connect your call. Goodbye.",
    },
    "es": {
        "action_prompt": (
            "Para escuchar un breve mensaje de audio, presione 1. "
            "Para hablar con un asociado, presione 2."
        ),
        "invalid": "Selección no válida. Por favor, intente de nuevo.",
        "playing": "Reproduciendo su mensaje de audio.",
        "after_audio": "Volviendo al menú principal.",
        "connecting": "Por favor espere mientras le conectamos con un asociado.",
        "dial_failed": "No pudimos conectar su llamada. Adiós.",
    },
}
