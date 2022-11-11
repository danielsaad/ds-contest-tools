SRC_DIR := src
BIN_DIR := bin
DBG_DIR := bin/debug

SRC := $(wildcard $(SRC_DIR)/*.cpp)
BIN := $(patsubst $(SRC_DIR)/%.cpp, $(BIN_DIR)/%, $(SRC))
DBG := $(patsubst $(SRC_DIR)/%.cpp, $(DBG_DIR)/%, $(SRC))

CXX := g++
CXX_FLAGS := -Wall -O2
BOCA_FLAGS := -static -DBOCA_SUPPORT
DEBUG_FLAGS := -Wall -g

.PHONY: all debug release clean

all: debug release

debug: $(DBG) $(DBG_DIR)/checker-boca

release: $(BIN) $(BIN_DIR)/checker-boca

$(BIN): $(BIN_DIR)/% : $(SRC_DIR)/%.cpp | $(BIN_DIR)
	$(CXX) $(CXX_FLAGS) $^ -o $@

$(DBG): $(DBG_DIR)/% : $(SRC_DIR)/%.cpp | $(DBG_DIR)
	$(CXX) $(DEBUG_FLAGS) $^ -o $@

$(BIN_DIR):
	mkdir -p $@

$(DBG_DIR):
	mkdir -p $@

$(BIN_DIR)/checker-boca: $(SRC_DIR)/checker.cpp
	$(CXX) $(CXX_FLAGS) $(BOCA_FLAGS) $^ -o $@ 

$(DBG_DIR)/checker-boca: $(SRC_DIR)/checker.cpp
	$(CXX) $(DEBUG_FLAGS) $(BOCA_FLAGS) $^ -o $@ 

clean:
	@echo Cleaning problem files
	rm -rf bin
