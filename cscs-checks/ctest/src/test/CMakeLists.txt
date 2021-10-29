add_executable(ok.exe 0.cpp)
add_test(NAME returnT COMMAND ok.exe)

add_executable(ko.exe 1.cpp)
add_test(NAME returnF COMMAND ko.exe)
