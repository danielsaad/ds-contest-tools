#! usr/bin/bash

# Generate executables
(cd src && make -j)

# Move checker executable
(mv src/checker .)

# Paths to be used
tests_folder="src/tests"
tmp_folder="src/tmp"
script_path="src/script.sh"

# Create temporary folders
mkdir -p "$tests_folder"
mkdir -p "$tmp_folder"

# Generate problem input from scripts
if [[ -f "$script_path" ]]
then
	outfile="teste"
    index=`(cd "$tmp_folder" && ls -l | wc -l)`
    while IFS= read -r line; do
        (cd "$tmp_folder" && ../$line > "$outfile")
        # Move only created file if it is not a multigenerator
        if [[ -s "$tmp_folder"/"$outfile" ]]; then
            mv "$tmp_folder"/"$outfile" "$tests_folder"/"$index"
            ((index++))
        # Move all files of the multigenerator
        else
            (cd "$tmp_folder" && rm "$outfile")
            for item in "$tmp_folder"/*
            do
                mv "$item" "$tests_folder"/"$index"
                ((index++))
            done
        fi
    done < "$script_path"
fi


# Add leading zeros to files
for testcase in $tests_folder/*
do
    old_name="$(basename $testcase)"
    new_name=`printf %03d ${old_name}`
    mv "$tests_folder"/"$old_name" "$tests_folder"/"$new_name" 2>/dev/null
done

# Move files and rename them
index=1
for testcase in $tests_folder/*
do
    test_name=$(basename $testcase)
    zero_index=`printf %03d ${index}`
    # Check next index not used
    while [ -f "$zero_index".in ]
    do
        ((index++))
        zero_index=`printf %03d ${index}`
    done
    mv "$tests_folder"/"$test_name" "$zero_index".in
done

# Generate output of tests
for input_file in *.in
do
    ./src/main_solution < $input_file > "$(basename $input_file .in)".out
done

# Remove items created
rm -rf "$tests_folder"
rm -rf "$tmp_folder"
(cd src && make clean)