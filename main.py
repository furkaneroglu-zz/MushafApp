import flet as ft
import sqlite3
import os
import g4f

# ==========================================
# 1. 114 SURENİN TAM LİSTESİ (v0.01 Güncel)
# ==========================================
SURE_ISIMLERI = {
    1: "Fâtiha", 2: "Bakara", 3: "Âl-i İmrân", 4: "Nisâ", 5: "Mâide", 6: "En'âm", 7: "A'râf", 8: "Enfâl", 9: "Tevbe", 10: "Yûnus",
    11: "Hûd", 12: "Yûsuf", 13: "Ra'd", 14: "İbrâhîm", 15: "Hicr", 16: "Nahl", 17: "İsrâ", 18: "Kehf", 19: "Meryem", 20: "Tâhâ",
    21: "Enbiyâ", 22: "Hac", 23: "Mü'minûn", 24: "Nûr", 25: "Furkân", 26: "Şuarâ", 27: "Neml", 28: "Kasas", 29: "Ankebût", 30: "Rûm",
    31: "Lokmân", 32: "Secde", 33: "Ahzâb", 34: "Sebe'", 35: "Fâtır", 36: "Yâsîn", 37: "Saffât", 38: "Sâd", 39: "Zümer", 40: "Mü'min",
    41: "Fussilet", 42: "Şûrâ", 43: "Zuhruf", 44: "Duhân", 45: "Câsiye", 46: "Ahkâf", 47: "Muhammed", 48: "Fetih", 49: "Hucurât", 50: "Kâf",
    51: "Zâriyât", 52: "Tûr", 53: "Necm", 54: "Kamer", 55: "Rahmân", 56: "Vâkıa", 57: "Hadîd", 58: "Mücâdele", 59: "Haşr", 60: "Mümtehine",
    61: "Saff", 62: "Cuma", 63: "Münâfikûn", 64: "Teğâbun", 65: "Talâk", 66: "Tahrîm", 67: "Mülk", 68: "Kalem", 69: "Hâkka", 70: "Meâric",
    71: "Nûh", 72: "Cin", 73: "Müzzemmil", 74: "Müddessir", 75: "Kıyâme", 76: "İnsân", 77: "Mürselât", 78: "Nebe'", 79: "Nâziât", 80: "Abese",
    81: "Tekvîr", 82: "İnfitâr", 83: "Mutaffifîn", 84: "İnşikâk", 85: "Burûc", 86: "Târık", 87: "A'lâ", 88: "Gâşiye", 89: "Fecr", 90: "Beled",
    91: "Şems", 92: "Leyl", 93: "Duha", 94: "İnşirâh", 95: "Tîn", 96: "Alak", 97: "Kadir", 98: "Beyyine", 99: "Zilzâl", 100: "Âdiyât",
    101: "Kâria", 102: "Tekâsür", 103: "Asr", 104: "Hümeze", 105: "Fîl", 106: "Kureyş", 107: "Mâûn", 108: "Kevser", 109: "Kâfirûn", 110: "Nasr",
    111: "Tebbet", 112: "İhlâs", 113: "Felak", 114: "Nâs"
}

# ==========================================
# 2. VERİTABANI MOTORU
# ==========================================
def verileri_cek(sure_no):
    base_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_path, "kuran_veri.db")
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT arapca, meal, ayet_no FROM Ayetler WHERE sure_no=? ORDER BY ayet_no", (sure_no,))
            return cur.fetchall()
    except Exception as e:
        print(f"[HATA]: {e}")
        return []

# ==========================================
# 3. ANA UYGULAMA (v0.01 KURALLARIYLA)
# ==========================================
def main(page: ft.Page):
    page.title = "Dijital Mushaf Asistanı"
    page.bgcolor = "black"
    page.theme_mode = "dark"
    page.padding = 15

    mushaf_alani = ft.ListView(expand=True, spacing=15)
    
    # Analiz Paneli
    analiz_yazisi = ft.Text("Sonuç bekleniyor...", size=16)
    alt_panel = ft.BottomSheet(
        ft.Container(
            padding=30, bgcolor="#1C1C1E",
            content=ft.Column([
                ft.Text("İLMİ ANALİZ", size=20, weight="bold", color="amber"),
                ft.Divider(),
                ft.Column([analiz_yazisi], scroll="auto", height=300)
            ])
        )
    )
    page.overlay.append(alt_panel)

    def analiz_tetikle(ayet, meal):
        analiz_yazisi.value = "Yapay zeka analiz ediyor... Lütfen bekleyin."
        alt_panel.open = True
        page.update()
        try:
            soru = f"Şu ayeti tefsir et: {ayet} - {meal}"
            cevap = g4f.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": soru}], stream=False)
            analiz_yazisi.value = cevap
        except:
            analiz_yazisi.value = "Bağlantı sorunu oluştu."
        page.update()

    def sayfayi_doldur(no):
        no = int(no)
        if no < 1: no = 1
        if no > 114: no = 114
        
        sure_input.value = str(no)
        mushaf_alani.controls.clear()
        veriler = verileri_cek(no)
        
        if not veriler:
            mushaf_alani.controls.append(ft.Text("VERİ ÇEKİLEMEDİ!", color="red"))
            page.update()
            return

        # BAŞLIK (İSİM + NO)
        sure_adi = SURE_ISIMLERI.get(no, "Sure")
        mushaf_alani.controls.append(
            ft.Row([
                ft.Text(f"{no}. {sure_adi} Suresi", size=28, color="amber", weight="bold")
            ], alignment="center")
        )

        tam_arapca = "".join([f"{a} ({n}) " for a, m, n in veriler])
        mushaf_alani.controls.append(ft.Text(tam_arapca, size=32, text_align="right"))
        mushaf_alani.controls.append(ft.Divider())

        for arapca, meal, ayet_no in veriler:
            mushaf_alani.controls.append(
                ft.Container(
                    padding=15, bgcolor="#1C1C1E", border_radius=10,
                    content=ft.Column([
                        ft.Text(f"{ayet_no}. {meal}", size=18),
                        ft.Row([
                            ft.ElevatedButton(
                                content=ft.Text("ANALİZ ET", color="amber"),
                                on_click=lambda e, a=arapca, m=meal: analiz_tetikle(a, m)
                            )
                        ], alignment="end")
                    ])
                )
            )
        page.update()

    def sure_atla(adim):
        mevcut = int(sure_input.value)
        sayfayi_doldur(mevcut + adim)

    # --- ÜST MENÜ ---
    sure_input = ft.TextField(value="1", width=60, text_align="center")
    
    # v0.01 kuralları: Sadece 'content' ve string hizalama
    page.add(
        ft.Row([
            ft.Text("MUSHAF", size=22, weight="bold"),
            ft.Row([
                ft.ElevatedButton(
                    content=ft.Text("<", size=20, weight="bold"),
                    on_click=lambda _: sure_atla(-1),
                    bgcolor="#1C1C1E"
                ),
                sure_input,
                ft.ElevatedButton(
                    content=ft.Text(">", size=20, weight="bold"),
                    on_click=lambda _: sure_atla(1),
                    bgcolor="#1C1C1E"
                ),
                ft.ElevatedButton(
                    content=ft.Text("GİT", color="black"),
                    bgcolor="amber",
                    on_click=lambda _: sayfayi_doldur(sure_input.value)
                )
            ], spacing=5)
        ], alignment="spaceBetween"),
        mushaf_alani
    )

    sayfayi_doldur("1")

if __name__ == "__main__":
    ft.app(target=main)