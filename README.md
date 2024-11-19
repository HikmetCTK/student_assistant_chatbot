Hackathon eğitim alanında yaptığım yapay zeka projesi. Öğrencilerin  Kendi seviyesine Uygun kaynağı aramak için dakikalarca video izlemesine gerek yok. Türkçe altyazıya sahip istediğiniz videonun linkini verdiğiniz anda sizin için kolaydan zora doğru video da geçen kaynakların sıralamasını yapıyor.  

Ayrıca öğrenciler, belli bir konuda kişisel plan oluşturmak isterlerse,'Çalışma Planı Oluştur' kısmından Kişiye özel bir çok seçenekle haftalık aylık gibi planlar oluşturabiliyor. İsterseniz planınızı güncelleyebilir veya indirebilirsiniz

Çalışma planı oluşturan ajanın oluşturduğu planda her konunun yanında konuyla alakalı  videonun linki öneriliyor . 


![Screenshot 2024-11-05 223731](https://github.com/user-attachments/assets/016fe2bc-93c0-4985-86e2-74ec846cf7dc)
![Screenshot 2024-11-05 180123](https://github.com/user-attachments/assets/6ccc53e1-2ca5-4bb1-87fe-5338ad5ec3a1)


Kullandığım kütüphaneler:

-google.generativeai(gemini-1.5-flash)==0.8.3

-youtube_transcript_api(Youtube videosundaki altyazılar)

-youtubesearchpython(youtube videolarını listeler)

-streamlit(arayüz)==1.24.0

-json==2.0.9

*** Önemli noktalar ***

-Her 2 ajan için de Gemini system instruction kısmında 'Few-shot learning' tekniğini kullandım. Modelin örnek çıktı sağlaması ve sınırlarını bilmesinde sıkça kullanılan bir teknik
 
-Kullanmak için:

Gerekli kütüphaneleri indirdikten sonra size özel 'Gemini api key' 'inizi  '.env' dosyasına yazıp  terminali açıp  'streamlit run helper.py' yazarak çalıştırıp kullanabilirsiniz.
