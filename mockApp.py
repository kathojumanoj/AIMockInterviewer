from flask import Flask, render_template,request,jsonify,make_response
import google.generativeai as genai
from PyPDF2 import PdfReader
from flask import session
import os

app=Flask(__name__)
app.secret_key = 'Mighty'
os.environ['GOOGLE_API_KEY']="Use Your Secrect API Key"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])


def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def extract_text_from_pdf(file_storage):
    pdf_file = file_storage.stream
    pdf_reader = PdfReader(pdf_file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

@app.route('/',methods=['GET','POST'])
def home():
  return render_template('./index_Mock.html')
@app.route('/upload',methods=['GET','POST'])
def resumeLoad():
   print("Uploaded")
   resume = request.files['resume_file']
   if resume:
      resumeName=resume.filename
      text=extract_text_from_pdf(resume)
      # print(text)
      session['resume']=text
      prompt_res="As a hr manager Generate interview questions from this resume only  five Questions : "+text
      res=get_gemini_response(prompt_res)
      res=res.split("\n")
      res = [i for i in res if i]
      # res.remove('')
      if len(res)>5:
         res.pop(0)

      for i in range(len(res)):
         res[i]=res[i].replace("*",'')
      session['res']=res
      # return '<h1>Welcome!!!<BR> '+ text +'<BR></h1>'
      return render_template('./upload.html', text=res)
   
@app.route('/score',methods=['GET','POST'])
def scoreResume():
   question = session.get('res')
   resume=session.get('resume')
   print(type(resume))
   scoreVal=[]
   answers=[]
   remarks=[]
   if request.method=='POST':
      for i in range(len(question)):
         que=question[i]
         answer=request.form['qans'+str(i+1)]
         answers.append(answer)
         if answer:
            prompt_marks="As a hr Manager you given question"+que+" based on "+resume +"and the user(Person) given answer "+answer+"then rate the answer out of 10 marks (only mark with digit) as output"
            resVal=get_gemini_response(prompt_marks)
            scoreVal.append(resVal)
         else:
            scoreVal.append(str(0))
      print(scoreVal)
      for i in range(len(scoreVal)):
         if len(scoreVal[i])>2:
            scoreVal[i]=str(scoreVal[:1])
            if scoreVal[i].isdigit():
               scoreVal[i]=int(scoreVal[i])
            else:
               break
         else:
            if(scoreVal[i].isdigit()):
               scoreVal[i]=int(scoreVal[i])
         if scoreVal[i]<=4:
            remarks.append("Very Poor Imporve Well!")
         elif scoreVal[i]>4 and scoreVal[i]<=7:
            remarks.append("Good Be Depth Knowledge in Topic")
         elif scoreVal[i]>7:
            remarks.append("Excellent Great Work...")
          

        
      print(question)
      # st='<br> 1'+ans1+'<br> 2'+ans2+'<br> 3'+ans3+'<br> 4'+ans4+"<br> 5"+ans5
      # return '<h3>'+st + '<br>'+str(question)+ '<br>'+ str(scoreVal) + '</h3'
      return render_template('score.html', questions=question, answers=answers, scores=scoreVal,remarks=remarks)
      # print(username, password)
app.run(debug=True)
