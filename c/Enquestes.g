grammar Enquestes;

chatbot: (conversation)+ enquesta EOF;

enquesta: ID DP ENQUESTA (ID)+ END;

conversation: (preg | resp | item | alternativa);

preg: (ID) DP PREGUNTA ID+ INTERROGANT;

resp: (ID) DP RESPOSTA opcio+;

opcio: NUM DP ID+ PIC;

item: ID DP ITEM ID IMPLICA ID;

alternativa: ID DP ALTERNATIVA ID CO alternatives CC;
 
alternatives: PO NUM COMA ID PC (COMA alternatives|);

PO : '(';
PC : ')';
CO : '[';
CC : ']';
COMA : ',';
DP : ':';
PIC : ';';
INTERROGANT : '?';
IMPLICA : '->';
PREGUNTA :'PREGUNTA';
RESPOSTA : 'RESPOSTA';
CONVERSATION : 'CONVERSATION';
ALTERNATIVA : 'ALTERNATIVA';
ENQUESTA : 'ENQUESTA';
ITEM : 'ITEM';
END : 'END';
NUM : [0-9]+ ;
ID : [a-zA-Z][a-zA-Z0-9\u0080-\u00FF]* ;

WS : [ \t\r\n\f]+ -> skip;
