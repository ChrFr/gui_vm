call conda create -n tdmks python=2.7
call activate tdmks
call conda install -y pyqt=4 
call conda install -y numpy
call conda install -y pytables
call conda install -y lxml
call python setup.py install
echo.
echo.
echo Installation der grafischen Oberflaeche beendet.
pause