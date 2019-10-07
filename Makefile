PDF = plongee_asynchrone.pdf
ZIP = plongee_asynchrone.zip
SRC = $(shell find src -name "*.md" | sort -n)

FLAGS =

GEN = $(PDF) $(ZIP)

$(PDF):	title.md $(SRC)
	pandoc -V lang=fr -V geometry:margin=1in -V colorlinks=true $^ -o $@ $(FLAGS)

$(ZIP): $(SRC)
	./gen_archive.py $@ $^

pdf: $(PDF)

zip: $(ZIP)

clean:
	rm -f $(GEN)

re:	clean $(GEN)

.PHONY:	clean re
