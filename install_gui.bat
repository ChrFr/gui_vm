call deactivate
call conda create -y -n gui_test python=2.7
call activate gui_test
call conda install -y pyqt=4 
call conda install -y numpy
call conda install -y pytables
call conda install -y lxml
call pip install gui_vm-0.74-py2-none-any.whl
echo.
echo.
echo Installation der grafischen Oberflaeche beendet.
pause