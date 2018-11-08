gcc -c ..\..\LAOU\utf8\utf8.c -o obj/utf8.o
g++ -c ..\..\LAOU\tsv_parser\static.cpp -o obj/static.o
g++ -c ..\..\LAOU\imdb_datasets\title.basics.cpp -o obj/title.basics.o
g++ -c -I ..\..\LAOU IMDB_tsv_Parser.cpp -o obj/IMDB_tsv_Parser.o
g++ obj/utf8.o obj/IMDB_tsv_Parser.o obj/title.basics.o obj/static.o -o a.exe