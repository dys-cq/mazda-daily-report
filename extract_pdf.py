import fitz

doc = fitz.open(r'C:\Users\Administrator\.openclaw\media\outbound\b8cafe51-a5fd-486a-b721-210be7bc4c20.pdf')
text = ''
for page in doc:
    text += page.get_text()
print(text)
