# Normal directories
SRC_DIR := src
BIN_DIR := bin
DBG_DIR := bin/debug

# Grader directories
GRADER := $(wildcard $(SRC_DIR)/grader.cpp)
GRADER_DIR := $(SRC_DIR)/grader
HANDLER_DIR := $(SRC_DIR)/handler

GRADER_SRC := $(wildcard $(GRADER_DIR)/*.cpp)
GRADER_BIN := $(patsubst $(GRADER_DIR)/%.cpp, $(BIN_DIR)/%, $(GRADER_SRC))
GRADER_DBG := $(patsubst $(GRADER_DIR)/%.cpp, $(DBG_DIR)/%, $(GRADER_SRC))

# Change CPP source directories if grader is defined
ifdef GRADER
	SRC := $(wildcard $(HANDLER_DIR)/*.cpp)
	BIN := $(patsubst $(HANDLER_DIR)/%.cpp, $(BIN_DIR)/%, $(SRC))
	DBG := $(patsubst $(HANDLER_DIR)/%.cpp, $(DBG_DIR)/%, $(SRC))
else
	SRC := $(wildcard $(SRC_DIR)/*.cpp)
	BIN := $(patsubst $(SRC_DIR)/%.cpp, $(BIN_DIR)/%, $(SRC))
	DBG := $(patsubst $(SRC_DIR)/%.cpp, $(DBG_DIR)/%, $(SRC))
endif

SRC_C := $(wildcard $(SRC_DIR)/*.c)
BIN_C := $(patsubst $(SRC_DIR)/%.c, $(BIN_DIR)/%, $(SRC_C))
DBG_C := $(patsubst $(SRC_DIR)/%.c, $(DBG_DIR)/%, $(SRC_C))

SRC_JAVA := $(wildcard $(SRC_DIR)/*.java)
BIN_JAVA := $(patsubst $(SRC_DIR)/%.java, $(BIN_DIR)/%.class, $(SRC_JAVA))
DBG_JAVA := $(patsubst $(SRC_DIR)/%.java, $(DBG_DIR)/%.class, $(SRC_JAVA))

C := gcc
CPP := g++
CXX_FLAGS := -Wall -O2
DEBUG_FLAGS := -Wall -g
BOCA_FLAGS := -static -DBOCA_SUPPORT

JV = javac
JV_DEBUG = -g
JV_DIR = -d bin
JV_DBG_DIR = -d bin/debug

.PHONY: all debug release clean

all: debug release

debug: $(DBG) $(DBG_C) $(DBG_JAVA) $(GRADER_DBG) $(DBG_DIR)/checker-boca 

release: $(BIN) $(BIN_C) $(BIN_JAVA) $(GRADER_BIN) $(BIN_DIR)/checker-boca

$(BIN): $(BIN_DIR)/% : $(SRC_DIR)/%.cpp | $(BIN_DIR)
	$(CPP) $(CXX_FLAGS) $^ -o $@

$(DBG): $(DBG_DIR)/% : $(SRC_DIR)/%.cpp | $(DBG_DIR)
	$(CPP) $(DEBUG_FLAGS) $^ -o $@

$(BIN_C): $(BIN_DIR)/% : $(SRC_DIR)/%.c | $(BIN_DIR)
	$(C) $(CXX_FLAGS) $^ -o $@

$(DBG_C): $(DBG_DIR)/% : $(SRC_DIR)/%.c | $(DBG_DIR)
	$(C) $(DEBUG_FLAGS) $^ -o $@

$(BIN_JAVA): $(BIN_DIR)/%.class : $(SRC_DIR)/%.java | $(BIN_DIR)
	$(JV) $(JV_DIR) $^

$(DBG_JAVA): $(DBG_DIR)/%.class : $(SRC_DIR)/%.java | $(DBG_DIR)
	$(JV) $(JV_DEBUG) $(JV_DBG_DIR) $^ 

$(GRADER_BIN): $(BIN_DIR)/% : $(GRADER_DIR)/%.cpp
	$(CPP) $(CXX_FLAGS) $(GRADER) $^ -o $@

$(GRADER_DBG): $(DBG_DIR)/% : $(GRADER_DIR)/%.cpp 
	$(CPP) $(DEBUG_FLAGS) $(GRADER) $^ -o $@

$(BIN_DIR):
	mkdir -p $@

$(DBG_DIR):
	mkdir -p $@

$(BIN_DIR)/checker-boca: $(SRC_DIR)/checker.cpp
	$(CPP) $(CXX_FLAGS) $(BOCA_FLAGS) $^ -o $@ 

$(DBG_DIR)/checker-boca: $(SRC_DIR)/checker.cpp
	$(CPP) $(DEBUG_FLAGS) $(BOCA_FLAGS) $^ -o $@ 

clean:
	@echo Cleaning problem files
	rm -rf bin
