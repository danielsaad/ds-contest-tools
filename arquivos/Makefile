.SILENT:

SRC_DIR := src
BIN_DIR := bin
INC_DIR := include

SRC := $(wildcard $(SRC_DIR)/*.cpp)
BIN := $(patsubst $(SRC_DIR)/%.cpp, $(BIN_DIR)/%, $(SRC))

CXX := g++
CXX_FLAGS := -Wall -I$(INC_DIR)
BOCA_FLAGS := -DBOCA_SUPPORT
DEBUG_FLAGS :=

.PHONY: all debug

all: $(BIN)

$(BIN): $(BIN_DIR)/% : $(SRC_DIR)/%.cpp | $(BIN_DIR)
	$(CXX) $(CXX_FLAGS) $(DEBUG_FLAGS) $^ -o $@ $(BOCA_FLAGS)

debug: DEBUG_FLAGS+=-g -O0 -DDEBUG
debug: all

$(BIN_DIR):
	mkdir -p $@

