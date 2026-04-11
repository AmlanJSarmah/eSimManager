# eSimInstaller
An application to install and configure eSim and it's various dependencies.   

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