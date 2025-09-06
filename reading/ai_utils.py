# reading/ai_utils.py
import os
from openai import OpenAI

def get_reading_feedback(book_title, pages_read, current_page, total_pages, streak):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # --- YENİ MANTIK BÖLÜMÜ ---
        progress_percent = int((current_page / total_pages) * 100)
        
        # İlerleme durumuna göre bir "durum metni" oluştur
        if progress_percent >= 100:
            reading_stage_feedback = "ve bu kitabı tamamen bitirdin!"
        elif progress_percent > 80:
            reading_stage_feedback = f"ve kitabın sonuna çok yaklaştın (şu an yaklaşık %{progress_percent} bitti)."
        elif progress_percent > 30:
            reading_stage_feedback = f"ve kitabın ortalarına geldin (şu an yaklaşık %{progress_percent} bitti)."
        elif progress_percent > 5:
            reading_stage_feedback = f"ve kitaba harika bir başlangıç yaptın (şu an yaklaşık %{progress_percent} bitti)."
        else:
            reading_stage_feedback = "ve bu kitaba ilk adımı attın!"
        # --- MANTIK BÖLÜMÜ SONU ---

        prompt = (
            f"Ben bir kitap okuma uygulaması kullanıcısıyım. '{book_title}' adlı kitabı okuyorum. "
            f"Bugün {pages_read} sayfa okudum. Bu okumayla birlikte, {reading_stage_feedback} "
            f"Ayrıca, {streak} gündür aralıksız okuma yapıyorum. "
            f"Bu duruma özel, Türkçe dilinde, arkadaş canlısı, kısa (en fazla 2 cümle), "
            f"motive edici ve kişiselleştirilmiş bir geri bildirim mesajı yazar mısın?"
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sen kullanıcıları kitap okuma yolculuklarında onlara özel durumları fark edip takdir eden pozitif bir okuma koçusun."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=70,
            temperature=0.8, # Yaratıcılığı biraz daha artırabiliriz
        )
        
        feedback = completion.choices[0].message.content.strip()
        return feedback
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "Harika bir ilerleme, böyle devam et!"

def generate_reading_plan(book_title, author, total_pages, days_to_finish):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Yazar bilgisini prompt'a ekliyoruz ki AI daha bilgili olsun
        author_info = f" (Yazar: {author})" if author else ""

        if not days_to_finish or days_to_finish <= 0:
            prompt = (
                f"'{book_title}'{author_info} adlı kitaba başlayacak bir kullanıcı için, Türkçe dilinde, arkadaş canlısı, "
                f"kısa (en fazla 3 cümle), motive edici kitapla ilgili bilgi vererek başlangıç mesajı yazar mısın? "
                f"Kullanıcının bir hedef tarihi belirlemediğini unutma."
            )
        else:
            avg_pages = round(total_pages / days_to_finish)
            prompt = (
                f"'{book_title}'{author_info} adlı {total_pages} sayfalık kitaba başlayacak ve {days_to_finish} günde bitirmeyi hedefleyen "
                f"bir kullanıcı için, Türkçe dilinde, arkadaş canlısı, kısa (en fazla 3 cümle), motive edici bir "
                f"başlangıç planı paragrafı yazar mısın? Günde ortalama {avg_pages} sayfa okuması gerektiğini "
                f"de belirterek onu bu maceraya teşvik et. Kesin bir takvim verme, sadece başlangıç motivasyonu sağla. Kitapla ilgili bilgi ver."
            )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sen kullanıcıları kitap okumaya teşvik eden, planlama yapan ve yol gösteren pozitif bir okuma koçusun."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        
        plan = completion.choices[0].message.content.strip()
        return plan
    except Exception as e:
        print(f"OpenAI API Error for Plan Generation: {e}")
        return "Bu yeni kitap maceranda harika bir başlangıç yapman dileğiyle! İstikrarlı bir şekilde her gün okumaya çalış."