from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ui import auth


def test_three_users_share_the_password():
    for name in ("sangamesh", "aditya", "udaykumar"):
        assert auth.verify(name, "test@123").username == name


def test_username_is_case_insensitive_and_trimmed():
    assert auth.verify("  Sangamesh ", "test@123").first_name == "Sangamesh"


def test_wrong_password_or_unknown_user_fails():
    assert auth.verify("sangamesh", "Test@123") is None
    assert auth.verify("sangamesh", "") is None
    assert auth.verify("nobody", "test@123") is None


def test_password_is_not_stored_in_plain_text():
    source = (ROOT / "ui" / "auth.py").read_text()
    assert "test@123" not in source


def test_display_names_and_initials():
    assert auth.USERS["sangamesh"].initials == "SK"
    assert auth.USERS["aditya"].initials == "AM"
    assert auth.USERS["udaykumar"].initials == "UD"
    assert auth.USERS["udaykumar"].first_name == "Udaykumar"


def test_token_round_trip_and_expiry():
    secret = b"k"
    token = auth.make_token("aditya", 2_000, secret)
    assert auth.read_token(token, now=1_000, secret=secret).username == "aditya"
    assert auth.read_token(token, now=3_000, secret=secret) is None          # expired


def test_token_cannot_be_forged_or_edited():
    secret = b"k"
    token = auth.make_token("aditya", 2_000, secret)
    user, exp, sig = token.split(".")
    assert auth.read_token(f"sangamesh.{exp}.{sig}", now=1_000, secret=secret) is None
    assert auth.read_token(f"{user}.9999999999.{sig}", now=1_000, secret=secret) is None
    assert auth.read_token(token, now=1_000, secret=b"other") is None
    assert auth.read_token("garbage", now=1_000, secret=secret) is None
    assert auth.read_token(None, now=1_000, secret=secret) is None


# ---- one-time pass used by the theme switch (works without cookies) -----------
def test_resume_pass_signs_back_in_once():
    key = b"k"
    token = auth.make_resume_token("aditya", now=1_000, key=key)
    assert auth.use_resume_token(token, now=1_010, key=key).username == "aditya"
    assert auth.use_resume_token(token, now=1_011, key=key) is None          # used already


def test_resume_pass_expires_quickly():
    key = b"k"
    token = auth.make_resume_token("aditya", now=1_000, key=key)
    assert auth.use_resume_token(token, now=1_000 + auth.RESUME_SECONDS + 1, key=key) is None


def test_resume_pass_cannot_be_forged():
    key = b"k"
    user, exp, nonce, sig = auth.make_resume_token("aditya", now=1_000, key=key).split(".")
    assert auth.use_resume_token(f"sangamesh.{exp}.{nonce}.{sig}", now=1_010, key=key) is None
    assert auth.use_resume_token(f"{user}.{exp}.{nonce}.{sig}", now=1_010, key=b"other") is None
    assert auth.use_resume_token("garbage", now=1_010, key=key) is None
    # a session cookie is not accepted as a pass, and a pass is not accepted as a cookie
    cookie = auth.make_token("aditya", 2_000, key)
    assert auth.use_resume_token(cookie, now=1_010, key=key) is None
    assert auth.read_token(auth.make_resume_token("aditya", now=1_000, key=key), now=1_010, secret=key) is None
