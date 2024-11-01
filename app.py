from flask import Flask, render_template, request, url_for, redirect, session
import GoogleNLPAPI as api
import getYoutubeVideoLinks as getYT
import emailer as email
import speech_recognition as sr
from emailAnalysis import send_email
import os

# import summarizer as summ


app = Flask(__name__)
app.secret_key = 'thisisasecretkey'


@app.route('/delallsessions')
def delallsessions():
    session.pop('transcript', None)
    session.pop('summary', None)
    session.pop('keywords', None)
    session.pop('email_sent', None)
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def index():
    # session.pop('transcript', None)
    # session.pop('summary', None)
    # session.pop('keywords', None)
    return render_template('index.html', session=session)


@app.route('/record')
def record():
    return render_template('record.html')


@app.route('/delsession', methods=['GET', 'POST'])
def delscript():
    session.pop('transcript', None)
    session.pop('summary', None)
    session.pop('keywords', None)
    return redirect('/convertwav')


@app.route('/textanalysis', methods=['GET', 'POST'])
def textanalysis():
    videos = []
    # people = []
    # places = []
    if 'transcript' in session:
        if request.method == 'POST':
            emailform = request.form
            reciever = emailform['email']
            subject = emailform['subject']
            send_email(f"{subject} - Your Lecture Analysis", session['transcript'], reciever,
                       'hackathon2021', 'rishabhbhandari6@gmail.com', session['videos'], session['keywords'])
        keywords = api.sample_analyze_entities(session['transcript'])
        session['keywords'] = keywords
        if 'keywords' in session:
            for catergory, keywords in session['keywords'].items():
                for keyword in keywords:
                    video = getYT.searchVideoForKeyword(keyword)
                    for indivvideo in video:
                        #     if catergory == "people":
                        #         people.append(f'{indivvideo}')
                        #     elif catergory == "placesOrOrganizations":
                        #         places.append(f'{indivvideo}')
                        videos.append(f'{indivvideo}')
            session['videos'] = videos
            length_keywords = len(session['keywords']['people']) + len(
                session['keywords']['placesOrOrganizations']) + len(session['keywords']['other'])
        return render_template('textanalysis.html', session=session, length_keywords=length_keywords)
    else:
        return redirect('/convertwav')


@app.route('/testintelligence', methods=['GET', 'POST'])
def testintelligence():
    if 'transcript' in session:
        if request.method == 'POST':
            emailform = request.form
            reciever = emailform['email']
            subject = emailform['subject']
            send_email(f"{subject} - Your Lecture Analysis", session['transcript'], reciever,
                       'hackathon2021', 'rishabhbhandari6@gmail.com')
        keywords = api.sample_analyze_entities(session['transcript'])
        session['keywords'] = keywords

        videos = []
        people = []
        places = []
        if 'keywords' in session:
            for catergory, keywords in session['keywords'].items():
                for keyword in keywords:
                    video = getYT.searchVideoForKeyword(keyword)
                    for indivvideo in video:
                        if catergory == "people":
                            people.append(f'{indivvideo}')
                        elif catergory == "placesOrOrganizations":
                            places.append(f'{indivvideo}')
                        videos.append(f'{indivvideo}')
        return render_template('testintelligence.html', session=session, videos=videos, places=places, people=people, lenplaces=len(places),
                               lenpeople=len(people))
    else:
        return redirect('/convertwav')


@app.route('/youtubevids')
def youtubevids():
    videos = []
    # people = []
    # places = []
    if 'keywords' in session:
        for catergory, keywords in session['keywords'].items():
            for keyword in keywords:
                video = getYT.searchVideoForKeyword(keyword)
                for indivvideo in video:
                    #     if catergory == "people":
                    #         people.append(f'{indivvideo}')
                    #     elif catergory == "placesOrOrganizations":
                    #         places.append(f'{indivvideo}')
                    videos.append(f'{indivvideo}')
        return render_template('videos.html', videos=videos)
    else:
        return redirect('/convertwav')


@app.route('/convertwav', methods=['GET', 'POST'])
def convertwav():
    transcript = ""
    if request.method == "POST":
        if "myfiles[]" not in request.files:
            return redirect(request.url)

        file = request.files["myfiles[]"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(file)
            with audioFile as source:
                recognizer.adjust_for_ambient_noise(source)
                data = recognizer.record(source)
            transcript = recognizer.recognize_google(data, key=None)
            session['transcript'] = transcript
            return redirect('/textanalysis')  # change in later/test

    return render_template('convertwav.html')


@app.route('/contactform', methods=['GET', 'POST'])
def contactform():
    session['valid'] = True
    contactform = request.form
    sender_email = contactform['email']
    subject = contactform['subject'] + f" by: {sender_email}"
    msg = contactform['message']
    if email == "" or subject == "" or msg == "":
        session['valid'] = False
    else:
        email.send_email(subject, msg, 'rishabhbhandari6@gmail.com',
                         'hackathon2021', 'rishabhbhandari6@gmail.com')
        session['email_sent'] = True
        return redirect('/#footer')
    return redirect('/#footer')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 9988))
    app.run(host='0.0.0.0', port=port)
