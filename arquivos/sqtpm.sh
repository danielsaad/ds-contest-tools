#! usr/bin/bash

# Generate executables
(cd src && make -j)

# Move checker executable
(mv src/checker .)

# Verify if there is not a DS generator
ds_generator=true
script_path="src/script.sh"
if [[ -f "$script_path" ]]
then
	# Read script lines
	while IFS= read -r line; do
		# Get generator name
    	set -- $line

		# Check for a DS generator
		if [[ "$1" == "generator" ]]
		then
			ds_generator=false
		fi
	done < "$script_path"
fi

# Create temporary directory
(cd src && mkdir -p tmp)

# Generate problem input from DS generator
generator_path="src/generator.cpp"
if [[ -f "$generator_path" ]] && $ds_generator
then
	(cd src/tmp && ../generator)
fi

# Generate problem input from scripts
if [[ -f "$script_path" ]]
then
	index=`(cd src/tmp && ls -l | wc -l)`
	while IFS= read -r line; do
		(cd src && ./$line > tmp/"$index")
		((index++))
	done < "$script_path"
fi

# Add leading zeros to files
tests_path="src/tmp"
for testcase in $tests_path/*
do
	old_name="$(basename $testcase)"
	new_name=`printf %03d ${old_name}`
	mv "$tests_path"/"$old_name" "$tests_path"/"$new_name" 2>/dev/null
done

# Move files and rename them
index=1
for testcase in $tests_path/*
do
	test_name=$(basename $testcase)
	zero_index=`printf %03d ${index}`
	# Check next index not used
	while [ -f "$zero_index".in ]
	do
		((index++))
		zero_index=`printf %03d ${index}`
	done
	mv "$tests_path"/"$test_name" "$zero_index".in
done

# Generate output of tests
for input_file in *.in
do
	./src/main_solution < $input_file > "$(basename $input_file .in)".out
done

# Remove items created
rm -rf "$tests_path"
(cd src && make clean)
