import re

with open('templates/base.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Reemplazar :root
old_root = r"""        :root {
            --primary-bg: #0f172a;
            --secondary-bg: #1e293b;
            --accent-color: #38bdf8;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --header-bg: #1e3a8a;
            /\* Azul oscuro como la imagen \*/
            --success: #22c55e;
            --error: #ef4444;
            --warning: #f59e0b;
        }"""
new_root = """        :root {
            --primary-bg: #004D71;
            --secondary-bg: #00829B;
            --accent-color: #78DED4;
            --text-main: #f8fafc;
            --text-dim: #D1F2EB;
            --header-bg: #003650;
            --success: #22c55e;
            --error: #ef4444;
            --warning: #f59e0b;
        }"""
html = re.sub(old_root, new_root, html)

# Reemplazar rgba del acento viejo (56, 189, 248) -> nuevo (120, 222, 212)
html = html.replace('rgba(56, 189, 248', 'rgba(120, 222, 212')
# Reemplazar viejo hex del acento general
html = html.replace('#38bdf8', '#78DED4')

# Reemplazar el viejo .btn-vibrant
html = html.replace('linear-gradient(135deg, #0ea5e9, #3b82f6)', 'linear-gradient(135deg, #00829B, #78DED4)')
html = html.replace('linear-gradient(135deg, #38bdf8, #60a5fa)', 'linear-gradient(135deg, #78DED4, #00829B)')

# Reemplazar hover states u otros colores hardcodeados de las barras
html = html.replace('linear-gradient(135deg, #0ea5e9, #38bdf8)', 'linear-gradient(135deg, #00829B, #78DED4)')
html = html.replace('linear-gradient(135deg, #6366f1, #818cf8)', 'linear-gradient(135deg, #004D71, #00829B)') # Barras del rival

# Opciones de Glassmorphism background oscuro del anterior
html = html.replace('rgba(30, 41, 59,', 'rgba(0, 77, 113,')

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('base.html colors replaced')
