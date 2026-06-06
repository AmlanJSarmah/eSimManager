# eSimManager
An application to install and configure eSim and it's various dependencies.   

## Links
Walkthrough https://youtu.be/SZHgf7i0jHA

## Dependencies
Esim works on both windows and linux but it has not been extensively tested for other linux distros except Ubuntu.  
Other than that **python3** and **pip** are the only major dependencies.  
The other required python packages are in **requirements.txt**. We will have instructions to set up the project below.  

## Installtion Instructions
Below are the installation instructions for Ubuntu and Windows  

### Ubuntu
1. We will first download the source code via **git clone** or **http**.  
2. Navigate to the project root. After that we will create a virtual environement using the command  
```
python3 -m venv .app
```
3. Once the virtual env is created start it with  
```
source ./.app/bin/activate
```
4. Download the dependencies in requirements.txt using  
```
pip install -r requirements.txt
```
5. Finally run the project using  
```
python main.py
```

### Windows 
1. We will first download the source code via **git clone** or **http**.  
2. Navigate to the project root. After that we will create a virtual environement using the command  
```
python3 -m venv .app
```
3. Once the virtual env is created start it with  
```
.\.app\Scripts\activate
```
4. Download the dependencies in requirements.txt using  
```
pip install -r requirements.txt
```
5. Finally run the project using  
```
python main.py
```

## Working  
### Installing eSim from scratch  

<img width="808" height="626" alt="1 ESim Installation" src="https://github.com/user-attachments/assets/50066e34-7980-4156-820d-23a1d8a364fe" />
<img width="1920" height="1080" alt="2 Running install script" src="https://github.com/user-attachments/assets/9f99c106-efa3-43e0-864e-f697f3c7ac28" />

### Installing Missing dependencies  

<img width="1876" height="1048" alt="4 Removing Dependency" src="https://github.com/user-attachments/assets/475cb9a0-c04f-48d0-88ac-b0e67db241d8" />
<img width="808" height="626" alt="5 Installing missing dependency" src="https://github.com/user-attachments/assets/7a09127d-1321-4396-88bf-f45e392ace66" />
<img width="1920" height="1080" alt="6 After installing dependency" src="https://github.com/user-attachments/assets/b21e1124-8dd2-454d-a936-2742620499a5" />
