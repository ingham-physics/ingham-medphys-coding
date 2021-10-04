# Ingham Medical Physics Coding Challenge

## Janet Cui workload 

## 1. Create dash-env 
conda create -n dash-dev python=3.7 -y

## 2. Activate dash-env
conda activate dash-dev

## 3. Make sure to run python file under "src" file
cd ingham-medphys-coding <br />
cd src

## 4. Download dash module, dash-bootstrap-components, pandas
pip install dash -U <br />
pip install dash-bootstrap-components <br />
pip install pandas

## 5. Run python file
python3 challenge_september_2021.py

## 6. Open the URL shows in Terminal (copy and paste it in Google Chrome)
e.g.,"Dash is running on http://127.0.0.1:8050/" 

## (7. If error shows address occupied, it needs to kill current process on terminal, and redo step6)
pkill -9 python
