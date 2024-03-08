# Standard directories
SRC_DIR := src
BIN_DIR := bin
DBG_DIR := bin/debug

# Get files
SRC := $(wildcard $(SRC_DIR)/*.cpp)
BIN := $(patsubst $(SRC_DIR)/%.cpp, $(BIN_DIR)/%, $(SRC))
DBG := $(patsubst $(SRC_DIR)/%.cpp, $(DBG_DIR)/%, $(SRC))

SRC_C := $(wildcard $(SRC_DIR)/*.c)
BIN_C := $(patsubst $(SRC_DIR)/%.c, $(BIN_DIR)/%, $(SRC_C))
DBG_C := $(patsubst $(SRC_DIR)/%.c, $(DBG_DIR)/%, $(SRC_C))

SRC_JAVA := $(wildcard $(SRC_DIR)/*.java)
BIN_JAVA := $(patsubst $(SRC_DIR)/%.java, $(BIN_DIR)/%.class, $(SRC_JAVA))
DBG_JAVA := $(patsubst $(SRC_DIR)/%.java, $(DBG_DIR)/%.class, $(SRC_JAVA))

CHECKER := $(wildcard $(SRC_DIR)/checker.cpp)

C := gcc
CPP := g++
CXX_FLAGS := -Wall -O2
DEBUG_FLAGS := -Wall -g
BOCA_FLAGS := -static -DBOCA_SUPPORT

JV = javac
JV_DEBUG = -g
JV_DIR = -d bin
JV_DBG_DIR = -d bin/debug

.PHONY: all debug release checker clean

all: debug release checker

debug: $(DBG) $(DBG_C) $(DBG_JAVA)

release: $(BIN) $(BIN_C) $(BIN_JAVA)

ifdef CHECKER
checker: $(DBG_DIR)/checker-boca $(BIN_DIR)/checker-boca
endif

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
