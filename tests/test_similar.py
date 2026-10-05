from core.similar import find_similar

# real titles from the two test videos, so the test does not need to rebuild the sections (about 45 seconds each)
SAMPLES = {
    "English": (
        "Every PC Component Explained in 10 minutes",
        ["CPU: The Brain of the Computer", "RAM and Its Function", "Storage Types Explained",
         "SSDs vs HDDs and GPU Basics", "GPU and Motherboard Overview", "PSU: The Heart of a PC",
         "PC Cooling Methods", "Supporting Cast Overview", "PC Components Summary"],
        "en",
    ),
    "Arabic": (
        "الخريطة في حياتنا | شرح الدرس الثاني دراسات اجتماعية رابعة ابتدائي مع حل تقييمات الدرس",
        ["شرح خريطة من منظور الطيران", "شرح الخريطة", "شرح عن عناصر الخرائط", "مفاتيح الخرائط ومقياس الرسم", "مقياس الخريطة"],
        "ar",
    ),
}

for name, (title, section_titles, language) in SAMPLES.items():
    sections = [{"title": t} for t in section_titles]
    result = find_similar(title, sections, language, video_id="none")
    print(f"\n=== {name}\nsearched for: {result['keywords']}")
    for video in result["videos"]:
        print(f" - {video['title']}  [{video['channel']}]  {video['url']}")
    if not result["videos"]:
        print(" (no videos found)")