import cv2
import numpy as np
import face_recognition
import os
import streamlit as st
import requests
from streamlit_lottie import st_lottie
from datetime import datetime
import pyrebase
firebaseConfig = {
  'apiKey': "AIzaSyDgyVz9paoJZXFgx7GtNkBBhdM_d_E5H0c",
  'authDomain': "facerecognition-d3374.firebaseapp.com",
  'projectId': "facerecognition-d3374",
  'databaseURL': "https://facerecognition-d3374-default-rtdb.europe-west1.firebasedatabase.app/",
  'storageBucket': "facerecognition-d3374.appspot.com",
  'messagingSenderId': "961273092616",
  'appId': "1:961273092616:web:3af991135331c255750fbd",
  'measurementId': "G-CP8V21PQ1B"
}
# Find more emojis here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Face Recogniion System", page_icon=":tada:", layout="wide")

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def attendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            time_now = datetime.now()
            tStr = time_now.strftime('%H:%M:%S')
            dStr = time_now.strftime('%d/%m/%Y')
            f.writelines(f'\n{name},{tStr},{dStr}')

lottie_coding = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")

# ---- HEADER SECTION ----
with st.container():
    st.subheader("Hello, I am Digvijay :wave:")
    st.title("A Second year Under graduate Student of IIT kharagpur")
    st.write(
        "I am really Interesed in the field of software Development and Technology and is really looking positively towards contributing in this field ."
    )
    st.write("[Learn More >](https://www.linkedin.com/in/digvijay-singh-thakur-27a7b1219/)")



with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        st.header("What is Project is about")
        st.write("##")
        st.write(
            """
            This is a web Based applcation which primarily works on making attendence using facal recognition for a given dataset.
            The python libraries which Ihave used while making this project are OpenC, face_recognition,dlib and som other small libraries
            """
        )
     
    with right_column:
        st_lottie(lottie_coding, height=300, key="coding")

with st.container():

    st.title("Face Recognition System")
    run = st.checkbox('Run')
    FRAME_WINDOW = st.image([])
    path = 'Images'
    images = []
    personName = []
    myList = os.listdir(path)
    # print(myList)

    for cu_img in myList:
        current_img = cv2.imread(f'{path}/{cu_img}')
        images.append(current_img)
        personName.append(os.path.splitext(cu_img)[0])
    # print(personName)

    def faceEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    encodeListKnown = faceEncodings(images)
    print("All Encodings Completed!!!")
 
    camera = cv2.VideoCapture(0)

    while run:
        ret, frame = camera.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = cv2.resize(frame, (0,0), None, 0.25, 0.25)
        faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

        facesCurrentFrame = face_recognition.face_locations(faces)
        encodeCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)

        for encodeFace, faceLoc in zip(encodeCurrentFrame, facesCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = personName[matchIndex].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0), 2)
                cv2.rectangle(frame, (x1, y2-35), (x2,y2), (0,255,0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                attendance(name)
        FRAME_WINDOW.image(frame)

    else:
        st.write('Stopped')

with st.container():
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    db = firebase.database()
    storage = firebase.storage()
    #st.sidebar.title("Our community app")
    choice = st.selectbox('login/Signup', ['Login', 'Sign up'])

    # Obtain User Input for email and password
    email = st.text_input('Please enter your email address')
    password = st.text_input('Please enter your password',type = 'password')

    # Sign up Block
    if choice == 'Sign up':
        handle = st.text_input(
            'Please input your app handle name', value='Default')
        submit = st.button('Create my account')

        if submit:
            user = auth.create_user_with_email_and_password(email, password)
            st.success('Your account is created suceesfully!')
            st.balloons()
            # Sign in
            user = auth.sign_in_with_email_and_password(email, password)
            db.child(user['localId']).child("Handle").set(handle)
            db.child(user['localId']).child("ID").set(user['localId'])
            st.title('Welcome' + handle)
            st.info('Login via login drop down selection')

    # Login Block
    if choice == 'Login':
        login = st.checkbox('Login')
        if login:
            user = auth.sign_in_with_email_and_password(email,password)
            st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
            bio = st.radio('Jump to',['Home','Workplace Feeds', 'Settings'])
            
    # SETTINGS PAGE 
            if bio == 'Settings':  
                # CHECK FOR IMAGE
                nImage = db.child(user['localId']).child("Image").get().val()    
                # IMAGE FOUND     
                if nImage is not None:
                    # We plan to store all our image under the child image
                    Image = db.child(user['localId']).child("Image").get()
                    for img in Image.each():
                        img_choice = img.val()
                        #st.write(img_choice)
                    st.image(img_choice)
                    exp = st.beta_expander('Change Bio and Image')  
                    # User plan to change profile picture  
                    with exp:
                        newImgPath = st.text_input('Enter full path of your profile imgae')
                        upload_new = st.button('Upload')
                        if upload_new:
                            uid = user['localId']
                            fireb_upload = storage.child(uid).put(newImgPath,user['idToken'])
                            a_imgdata_url = storage.child(uid).get_url(fireb_upload['downloadTokens']) 
                            db.child(user['localId']).child("Image").push(a_imgdata_url)
                            st.success('Success!')           
                # IF THERE IS NO IMAGE
                else:    
                    st.info("No profile picture yet")
                    newImgPath = st.text_input('Enter full path of your profile image')
                    upload_new = st.button('Upload')
                    if upload_new:
                        uid = user['localId']
                        # Stored Initated Bucket in Firebase
                        fireb_upload = storage.child(uid).put(newImgPath,user['idToken'])
                        # Get the url for easy access
                        a_imgdata_url = storage.child(uid).get_url(fireb_upload['downloadTokens']) 
                        # Put it in our real time database
                        db.child(user['localId']).child("Image").push(a_imgdata_url)
    # HOME PAGE
            elif bio == 'Home':
                col1, col2 = st.beta_columns(2)
                
                # col for Profile picture
                with col1:
                    nImage = db.child(user['localId']).child("Image").get().val()         
                    if nImage is not None:
                        val = db.child(user['localId']).child("Image").get()
                        for img in val.each():
                            img_choice = img.val()
                        st.image(img_choice,use_column_width=True)
                    else:
                        st.info("No profile picture yet. Go to Edit Profile and choose one!")
                    
                    post = st.text_input("Let's share my current mood as a post!",max_chars = 100)
                    add_post = st.button('Share Posts')
                if add_post:   
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")              
                    post = {'Post:' : post,
                            'Timestamp' : dt_string}                           
                    results = db.child(user['localId']).child("Posts").push(post)
                    st.balloons()

                # This coloumn for the post Display
                with col2:
                    
                    all_posts = db.child(user['localId']).child("Posts").get()
                    if all_posts.val() is not None:    
                        for Posts in reversed(all_posts.each()):
                                #st.write(Posts.key()) # Morty
                                st.code(Posts.val(),language = '') 
            else:
                all_users = db.get()
                res = []
                # Store all the users handle name
                for users_handle in all_users.each():
                    k = users_handle.val()["Handle"]
                    res.append(k)
                # Total users
                nl = len(res)
                st.write('Total users here: '+ str(nl)) 
                
                # Allow the user to choose which other user he/she wants to see 
                choice = st.selectbox('My Collegues',res)
                push = st.button('Show Profile')
                
                # Show the choosen Profile
                if push:
                    for users_handle in all_users.each():
                        k = users_handle.val()["Handle"]
                        # 
                        if k == choice:
                            lid = users_handle.val()["ID"]
                            
                            handlename = db.child(lid).child("Handle").get().val()             
                            
                            st.markdown(handlename, unsafe_allow_html=True)
                            
                            nImage = db.child(lid).child("Image").get().val()         
                            if nImage is not None:
                                val = db.child(lid).child("Image").get()
                                for img in val.each():
                                    img_choice = img.val()
                                    st.image(img_choice)
                            else:
                                st.info("No profile picture yet. Go to Edit Profile and choose one!")
    
                            # All posts
                            all_posts = db.child(lid).child("Posts").get()
                            if all_posts.val() is not None:    
                                for Posts in reversed(all_posts.each()):
                                    st.code(Posts.val(),language = '')
