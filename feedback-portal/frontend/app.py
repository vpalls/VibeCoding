import requests
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "feedback-portal-secret-key"

API_BASE = "http://localhost:8000"


# ──────────────────────────────────────────────
# Page 1 – Customer Feedback Submission
# ──────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        payload = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "message": request.form.get("message", "").strip(),
            "rating": int(request.form.get("rating", 3)),
        }
        try:
            resp = requests.post(f"{API_BASE}/feedback", json=payload, timeout=5)
            resp.raise_for_status()
            flash("Thank you! Your feedback has been submitted successfully.", "success")
        except requests.exceptions.ConnectionError:
            flash("Cannot reach the backend. Make sure the FastAPI server is running.", "danger")
        except Exception as exc:
            flash(f"Submission failed: {exc}", "danger")

        return redirect(url_for("feedback"))

    return render_template("feedback.html")


# ──────────────────────────────────────────────
# Page 2 – Admin Response Dashboard
# ──────────────────────────────────────────────

@app.route("/admin")
def admin():
    feedbacks = []
    try:
        resp = requests.get(f"{API_BASE}/feedback", timeout=5)
        resp.raise_for_status()
        feedbacks = resp.json()
    except requests.exceptions.ConnectionError:
        flash("Cannot reach the backend. Make sure the FastAPI server is running.", "danger")
    except Exception as exc:
        flash(f"Error loading feedback: {exc}", "danger")

    return render_template("admin.html", feedbacks=feedbacks)


@app.route("/admin/respond/<int:feedback_id>", methods=["POST"])
def respond(feedback_id: int):
    response_text = request.form.get("response", "").strip()
    if not response_text:
        flash("Response cannot be empty.", "warning")
        return redirect(url_for("admin"))

    try:
        resp = requests.post(
            f"{API_BASE}/feedback/{feedback_id}/respond",
            json={"response": response_text},
            timeout=5,
        )
        resp.raise_for_status()
        flash("Response sent successfully!", "success")
    except requests.exceptions.ConnectionError:
        flash("Cannot reach the backend. Make sure the FastAPI server is running.", "danger")
    except Exception as exc:
        flash(f"Failed to send response: {exc}", "danger")

    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
