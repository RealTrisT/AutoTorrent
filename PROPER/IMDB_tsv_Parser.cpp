#include <stdio.h>
#include <string.h>
#include <stdlib.h>

extern "C"{
	#include "utf8/utf8.h"
}
#include "imdb_datasets/title.basics.hpp"
#include "tsv_parser/static.hpp"

#define maxEntrySize 1000

int main(int argc, char const *argv[]){

	FILE* fil = 0;

	fil = fopen(argv[1], "rb");
	if(!fil){puts("couldn't open file"); return 0;}

	StaticTsvArr tsv = StaticTsvArr(9, [](void*p)->void{free(p);});
	char buffer[maxEntrySize];

	////////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////////

	while(fgets(buffer, maxEntrySize, fil)){
		unsigned len = strlen(buffer);
		buffer[--len] = '\0'; //fgets gets the \n too
		char* alloct = (char*)malloc(len+1); memcpy(alloct, buffer, len+1);
		if(!tsv.feed(alloct))break;
	}

	unsigned totalSiz = tsv.size();
	printf("got %u entries\n", totalSiz);

	////////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////////

	TitleEntry* entries = (TitleEntry*)malloc(sizeof(TitleEntry)*totalSiz);

	for (unsigned i = 0; i < totalSiz; ++i){
		entries[i] = TitleEntry(
			(char*)tsv(i, 0), (char*)tsv(i, 1), 
			(unsigned char*)tsv(i, 2), (unsigned char*)tsv(i, 3), 
			(char*)tsv(i, 4), (char*)tsv(i, 5), (char*)tsv(i, 6), 
			(char*)tsv(i, 7), (char*)tsv(i, 8)
		);
	}

	printf("Proper format generated\n");

	////////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////////////////////////

	char RequestedName[200] = {0};
	char RequestedType[200] = {0};
	TitleEntry::TitleType tip = TitleEntry::TitleType::tINVALID;


	while(true){
		puts("Name search:");
		fgets(RequestedName, 200, stdin);RequestedName[strlen(RequestedName)-1] = 0;

		tip = TitleEntry::TitleType::tINVALID;
		do{
			puts("Type:");
			fgets(RequestedType, 200, stdin);RequestedType[strlen(RequestedType)-1] = 0;
			tip = TitleEntry::type(RequestedType);
		}while(tip == TitleEntry::TitleType::tINVALID);

		bool found = false;
		for (unsigned i = 0; i < totalSiz; ++i){
			char* title = (char*)entries[i].primaryTitle;
			if(!strcmp(title, RequestedName)){
				if(entries[i].titleType == tip){
				
					printf("IMDB ID: %u\n", entries[i].imdbID);
					printf("TYPE: %s\n", TitleEntry::titleTypeStrings[entries[i].titleType]);
					printf(entries[i].runtimeMinutes==0xFFFFFFFF?"RUNTIME: \\N\n":"RUNTIME: %u\n", entries[i].runtimeMinutes);
					puts("");

					found = true;
					break;
				}
			}
		}
		if(!found)puts("couldn't find yo shit");
	}

	return 0;
}