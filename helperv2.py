import google.generativeai as genai
import json
from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
from youtubesearchpython import VideosSearch
import re



import os

# Access the API key from the environment
api_key = os.getenv('API_KEY')


genai.configure(api_key=api_key)

generation_config={
    "temperature":0.2,
    "top_p":0.96,
    "top_k":64,
    "max_output_tokens":8192,
    "response_mime_type": "application/json"

}
class Agent:
    def __init__(self,name,role):
        self.name = name 
        self.role = role
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash",system_instruction=role)
        self.chat_session = self.model.start_chat()
    def generate_response_json(self,prompt):
        
        response=self.model.generate_content(prompt,generation_config=generation_config)
        return response.text
    def generate_response(self,prompt):
        
        response=self.model.generate_content(prompt )
        
        return response.text
    
def youtube_id_extract(youtube_link):
    #link=youtube_link[0][1].split("=")[1]  # taking youtube id  of first video from youtube links  list,
    id=youtube_link.split("=")[1]
    return id


def get_subtitles(video_id,language='tr'):
    try:
        # List all available transcripts for the video
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        
        auto_generated_subtitles = None
        
        for transcript in transcripts:
            #print(f"Language: {transcript.language}, Generated by YouTube: {transcript.is_generated}, Language code: {transcript.language_code}")
            if transcript.language == "Turkish (auto-generated)":
                    auto_generated_subtitles = transcript.fetch()
        
        if  auto_generated_subtitles:
            subtitles_text = ' '.join([entry['text'] for entry in auto_generated_subtitles])
            return subtitles_text
        else:
            print("lütfen altyazısı olan bir video seçiniz. O zaman yardımcı olabilirim")
        
        return None
        
    except Exception as e:
        print("Error:", e)
        return None

# Replace with your actual video ID

#subtitles = get_subtitles(video_id, language='eng')  # Set to 'tr' for Turkish
def source_lister(subtitles):
    effective_prompt="""
    Aşağıdaki metinde geçen kaynak kitapları ve test kitaplarını inceleyerek, her bir kitabın adını ve zorluk seviyesini ayırt et. Kitapları zorluk seviyelerine göre sınıflandır ve her bir kitap için ilgili bilgileri listele.
eğer videoda kaynak veya kitap adı geçmiyor farklı bir konuda konuşuluyorsa 'bu videoda kaynak önerisi yapılmamaktadır lütfen başka video seçiniz' de. 
    **Kitap Adı:**
* **Tür:** (Kaynak veya Test)
* **Zorluk Seviyesi:** (Çok Kolay, Kolay, Orta, Zor, Çok Zor)
* **Video Desteği:** (Var/Yok, Ayrıntılı bilgi veriniz: Kendi YouTube kanalı var mı, hangi konularda video destek sağlıyor gibi)
* **Özellikler:** (Kitabın içeriği, soru tipi, seviyesi, ek materyaller gibi)

**Örnek Çıktı:**

*** Kolay Kitaplar:***
    **Kitap Adı: 3-4-5 Kimya**
    * **Tür:** Test
    * **Zorluk Seviyesi:** Kolay
    * **Video Desteği:** Yok
    * **Özellikler:** Soru bankasıdır.

*** Orta Kitaplar:***
**Kitap Adı: Miray Kimya**
    * **Tür:** Kaynak
    * **Zorluk Seviyesi:** Orta
    * **Video Desteği:** Yok
    * **Özellikler:** Konu anlatımı ve sorular içerir. Kenarda ek bilgiler bulunur.

*** Zor Kitaplar:***
**Kitap Adı: Apotemi Kimya**
    * **Tür:** Kaynak
    * **Zorluk Seviyesi:** Zor
    * **Video Desteği:** Yok
    * **Özellikler:** Konu anlatımı ve sorular içerir. Kenarda ek bilgiler bulunur.

**Notlar:**
* Kitapların zorluk seviyesini belirlerken, metindeki ipuçlarını (örneğin, "temel bilgiler", "ileri düzey sorular") kullanın.
* Video desteği konusunda mümkün olduğunca detaylı bilgi verin. Örneğin, "Kendi YouTube kanalı var mı?", "Hangi konular için video çözümleri bulunuyor?" gibi soruların cevaplarını araştırabilirsiniz.
* Eğer bir kitap için yeterli bilgi yoksa, bunu belirtin (örneğin, "Zorluk seviyesi hakkında net bir bilgi bulunamadı").

**Ek Talimatlar:**
* **Zorluk Seviyesi Tanımları:** Farklı zorluk seviyelerini daha net bir şekilde tanımlayarak, ChatGPT'nin daha doğru bir değerlendirme yapmasını sağlayabilirsiniz.
* **Özelliklerin Ayrıntılandırılması:** Kitapların özelliklerini daha detaylı bir şekilde listeleyerek, kullanıcıya daha fazla bilgi verebilirsiniz. Örneğin, "soru tipi" yerine "çoktan seçmeli, doğru-yanlış, eşleştirme gibi" daha spesifik ifadeler kullanabilirsiniz."""

    source_lister=Agent("Lister of sources",effective_prompt)
    response=source_lister.generate_response(subtitles)
    return response
def get_youtube_video_link(query):
    # Perform the search
    videos_search = VideosSearch(query, limit=1)
    results = videos_search.result()  # Get the search results

    # Check if there are results
    if results['result']:
        video = results['result'][0]  # Get the first video
        link = f"https://www.youtube.com/watch?v={video['id']}"
        return link
    else:
        return "No videos found."  # Handle the case where no videos are found


def parse_json_response(result):
    # Parse the JSON response
    data = json.loads(result)

    # Prepare the output format
    output = []

    # Iterate through the weeks and topics
    for week, topics in data.items():
        output.append(f"{week.capitalize()}:")
        for topic in topics:
            video_link=get_youtube_video_link(topic['konu'])
            output.append(f"  Konu: {topic['konu']}  {video_link}")
            output.append(f"  Çalışma Saati: {topic['çalışma_saati']}")
            output.append(f"  Etkinlik: {topic['etkinlik']}")
            output.append("")  # Add a blank line for better separation

    # Join the output list into a single string
    formatted_output = "\n".join(output)
    return formatted_output
def planner(grade, subject, level, learning_type, time, destination):
    plan_maker_prompt = f"""Sen öğrencilerin hedefleri doğrultusunda verimli ve uygulanabilir plan hazırlayan asistansın. Aşağıdaki parametreleri baz alarak plan oluştur.
    Sınıf: {grade}
    Konu: {subject}
    Düzey: {level}
    Öğrenme stili: {learning_type}
    Zaman: {time}
    Hedef: {destination}
    
    Planda bulunması gerekenler:
    1. Öğrencinin istediği süreye göre (günlük, haftalık, aylık veya yıllık) belirli bir çalışma temposu ve rutin öner.
    Örneğin, günlük plan için saatlik dilimlere bölünmüş, haftalık plan için günlere ayrılmış öneriler sunabilirsin.
    2. Öğrencinin seçtiği düzeye  yönelik konularla ilgili taktik verebilirsin.
    *** Çıktı formatı:***
    **sadece  Json çıktısı olmalı**
    *ilk haftanın konuları,çalışma saati,ve etkinlik bilgilerini içermeli*
    *konuların başına kaçıncı sınıf olduğunu belirt*
    Olmaması gerekenler:
    ***Json çıktısı dışında herhangi bir şey ekleme**
    örnek çıktı:
{{
  "ilk_hafta": [
    {{
      "konu": "11. sınıf-Denklem Çözme",
      "çalışma_saati": "1 saat",
      "etkinlik": "Denklem çözme tekniklerini gözden geçirmek için konu videosu izledikten sonra soru çözün. Çözümlerinizi ayrıntılı olarak yazın ve çözüm adımlarını açıklayın."
    }},
    {{
      "konu": "11. sınıf-Fonksiyonlar",
      "çalışma_saati": "1 saat",
      "etkinlik": "Fonksiyon kavramını, yapısını anlamak için çeşitli soru tipleri çözün. \"YouTube\" platformunda fonksiyonlar hakkında görsel anlatımlı videolar izleyin."
    }}
  ],
  "ikinci_hafta": [
    {{
      "konu": "11. sınıf-Polinomlar",
      "çalışma_saati": "1 saat",
      "etkinlik": "Polinomların tanımını ve çeşitlerini öğrenmek için konu videoları izleyin. Çeşitli polinom örnekleri çözerek pekiştirme yapın."
    }},
    {{
      "konu": "11. sınıf-Üçgenler",
      "çalışma_saati": "1 saat",
      "etkinlik": "Üçgenlerin iç ve dış açılarının toplamını öğrenmek için ilgili kitaplardan alıştırmalar yapın. Ayrıca, üçgen eşitlikleri ile ilgili sorular çözün."
    }}
  ]
}}

    """

    planner_bot = Agent("Plan Maker", plan_maker_prompt)
    initial_plan = planner_bot.generate_response_json(plan_maker_prompt)
    
    try:
        # Ensure the response is valid JSON
        json.loads(initial_plan)
        return initial_plan
    except json.JSONDecodeError:
        return json.dumps({
            "ilk_hafta": [
                {"konu": "Hata", 
                 "çalışma_saati": "0 saat", 
                 "etkinlik": "Plan oluşturulurken bir hata oluştu. Lütfen tekrar deneyin."}
            ]
        }, ensure_ascii=False)

def update_plan(current_plan, update_prompt):
    """Function to update existing plan based on user input"""
    planner_bot = Agent("Plan updater", "Sen plan güncellemelerinden sorumlu bir asistansın.")
    try:
        current_plan_dict = json.loads(current_plan)
        updated_plan = planner_bot.generate_response_json(f"""
        Mevcut plan: {json.dumps(current_plan_dict, ensure_ascii=False)}
        Kullanıcı isteği: {update_prompt}
        """)
        
        # Ensure the response is valid JSON
        json.loads(updated_plan)
        return updated_plan
    except Exception as e:
        st.error(f"Plan güncellenirken bir hata oluştu: {str(e)}")
        return current_plan

def main():
    st.title("Öğrenci Dostu Bot")
    
    option = st.sidebar.selectbox(
        "İşlem Seçin",
        ["Kaynak Kitap Listeleyici", "Çalışma Planı Oluştur"]
    )
    st.write(f"Debug: Selected option is '{option}'")  # Debug statement
    # Add debug information
    st.sidebar.write(f"Selected option: {option}")

    if option == "Kaynak Kitap Listeleyici":
        # Previous code for option 1
        st.header("Youtube videosundaki Kaynak Kitapları zorluk sırasına göre listeler")
        link = st.text_input("Youtube linkini buraya yapıştır")
        if st.button("Listele"):
            id = youtube_id_extract(link)
            
            subtitle = get_subtitles(id)
            
            response = source_lister(subtitle)
            st.write(response)
    
    elif option == "Çalışma Planı Oluştur":
        st.header("Kişiselleştirilmiş Çalışma Planı Oluştur")
        
        with st.form(key="study_plan_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                grade = st.selectbox(
                    "Sınıf",
                    options=["9", "10", "11", "12"],
                    help="Öğrencinin sınıf seviyesini seçin"
                )
                
                subject = st.text_input(
                    "Konu",
                    placeholder="Örn: Matematik - Türev",
                    help="Çalışmak istediğiniz konuyu girin"
                )
                
                level = st.select_slider(
                    "Seviye",
                    options=["Çok Kolay", "Kolay", "Orta", "Zor", "Çok Zor"],
                    value="Orta",
                    help="Çalışma planının zorluk seviyesini seçin"
                )
            
            with col2:
                learning_type = st.selectbox(
                    "Öğrenme Tarzı",
                    options=["Görsel", "İşitsel", "Kinestetik", "Okuyarak"],
                    help="Size en uygun öğrenme tarzını seçin"
                )
                
                time = st.selectbox(
                    "Plan Süresi",
                    options=["Günlük", "Haftalık", "Aylık", "Dönemlik"],
                    help="Planın kapsayacağı süreyi seçin"
                )
                
                destination = st.text_input(
                    "Hedef",
                    placeholder="Örn: TYT'de ilk 10000'e girmek",
                    help="Ulaşmak istediğiniz hedefi belirtin"
                )
            
            submit_button = st.form_submit_button(
                label="Plan Oluştur",
                use_container_width=True
            )

        # If form is submitted, create initial plan
        if submit_button:
            if not all([subject, destination]):
                st.error("Lütfen konu ve hedef alanlarını doldurun!")
            else:
                try:
                    # Create and store the initial plan in session state
                    with st.spinner("Plan oluşturuluyor..."):
                        initial_plan = planner(grade, subject, level, learning_type, time, destination)
                        st.session_state.current_plan = initial_plan
                        st.markdown("### Oluşturulan Plan:")
                        st.markdown(parse_json_response(initial_plan))
                except Exception as e:
                    st.error(f"Plan oluşturulurken bir hata oluştu: {str(e)}")

        # Show update section only if we have a plan
        if 'current_plan' in st.session_state:
            st.markdown("---")
            st.markdown("### Planı Güncelle")
            
            update_prompt = st.text_area(
                "Planı nasıl güncellemek istersiniz?",
                placeholder="Örn: Matematik çalışma süresini artır veya konuları daha detaylı hale getir"
            )
            
            if st.button("Planı Güncelle"):
                if update_prompt:
                    try:
                        with st.spinner("Plan güncelleniyor..."):
                            updated_plan = update_plan(st.session_state.current_plan, update_prompt)
                            st.session_state.current_plan = updated_plan
                            st.markdown("### Güncellenmiş Plan:")
                            st.markdown(parse_json_response(updated_plan))
                    except Exception as e:
                        st.error(f"Plan güncellenirken bir hata oluştu: {str(e)}")
                else:
                    st.warning("Lütfen güncelleme için bir açıklama girin.")
            
            # Add download button for current plan
            st.download_button(
                label="Planı İndir",
                data=parse_json_response(st.session_state.current_plan),
                file_name="study_plan.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
