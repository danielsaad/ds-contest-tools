.SILENT:

SRC_DIR := src
BIN_DIR := bin

SRC := $(wildcard $(SRC_DIR)/*.cpp)
BIN := $(patsubst $(SRC_DIR)/%.cpp, $(BIN_DIR)/%, $(SRC))

CXX := g++
CXX_FLAGS := -Wall -O2
BOCA_FLAGS := -static -DBOCA_SUPPORT
DEBUG_FLAGS :=

.PHONY: all debug

all: $(BIN) $(BIN_DIR)/checker-boca

$(BIN): $(BIN_DIR)/% : $(SRC_DIR)/%.cpp | $(BIN_DIR)
	$(CXX) $(CXX_FLAGS) $(DEBUG_FLAGS) $^ -o $@

$(BIN_DIR):
	mkdir -p $@

$(BIN_DIR)/checker-boca: $(SRC_DIR)/checker.cpp
	$(CXX) $(CXX_FLAGS) $(DEBUG_FLAGS) $(BOCA_FLAGS) $^ -o $@ 

debug: DEBUG_FLAGS += -g -O0 -DDEBUG
debug: all
