from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Lista degli eventi
eventi = []

@app.route("/")
def index():
    return render_template("index.html", eventi=eventi)

@app.route("/aggiungi", methods=["POST"])
def aggiungi_evento():
    titolo = request.form.get("titolo")
    if titolo:  # Controlla che il titolo non sia vuoto
        eventi.append({"titolo": titolo})
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
