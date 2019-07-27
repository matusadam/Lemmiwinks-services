from sanic import Sanic

app = Sanic()

app.static('/', 'www/index.html', name='index_html')
app.static('/style.css', 'www/style.css', name='style_css')
app.static('/house.png', 'www/house.png', name='house_png')

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8000")


