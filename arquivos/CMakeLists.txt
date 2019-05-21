cmake_minimum_required(VERSION 2.8)
project ("II Maratona de Programação do IFB" CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


include_directories("${CMAKE_SOURCE_DIR}/include")

SET(CMAKE_VERBOSE_MAKEFILE on)
if(CMAKE_BUILD_TYPE MATCHES DEBUG)
	MESSAGE(STATUS "Debug mode")
    SET(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Wall")
    SET(INSTALL_DIR ${CMAKE_SOURCE_DIR}/bin/debug)
else()
	MESSAGE(STATUS "Release mode")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -Wall")
    SET(INSTALL_DIR ${CMAKE_SOURCE_DIR}/bin)
endif(CMAKE_BUILD_TYPE MATCHES DEBUG)

file(GLOB SRC
       "${CMAKE_SOURCE_DIR}/src/*.cpp"
)

message(${SRC})

foreach(f ${SRC})
    get_filename_component(barename ${f} NAME)
    if("${barename}" STREQUAL "checker.cpp")
        string(REPLACE ".cpp" "-boca" exe "${barename}")
        add_executable(${exe} "src/${barename}")
		target_compile_definitions(${exe} PRIVATE -DBOCA_SUPPORT)
	else()
        string(REPLACE ".cpp" "" exe "${barename}")
        add_executable(${exe} "src/${barename}")
    endif("${barename}" STREQUAL "checker.cpp")
    message(STATUS ${exe})
    install(TARGETS ${exe} DESTINATION ${INSTALL_DIR})
endforeach(f ${SRC})

