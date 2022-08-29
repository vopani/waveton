<div align='center'>

<h1>WaveTon</h1>
💯 Wave applications

<br>
<br>

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?logo=apache)](https://github.com/vopani/waveton/blob/master/LICENSE)
[![GitHub](https://img.shields.io/github/stars/vopani/waveton?color=yellowgreen&logo=github)](https://img.shields.io/github/stars/vopani/waveton?color=yellowgreen&logo=github)
[![Twitter](https://img.shields.io/twitter/follow/vopani)](https://twitter.com/vopani)

</div>

## NER Annotation 🖥️
Annotate entities for Named-Entity Recognition tasks.

![](demo.gif)

## Setup ⚙️
1. Check the version of Python, must be Python 3.9+ but recommended to use Python 3.10+ for best experience

```bash
python3 --version
```

2. Clone the repository

```bash
git clone https://github.com/vopani/waveton.git
```

3. Create a virtual environment

```bash
cd waveton/apps/data_apps/ner_annotation
python3 -m venv venv
source venv/bin/activate
```

4. Install the packages

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

5. Run the application

```bash
wave run app
```

6. View the application on your local browser: [http://localhost:10101](http://localhost:10101)
