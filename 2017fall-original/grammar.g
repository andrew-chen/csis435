start: expr* ;
@expr: atom | list ;
list: '\(' expr * '\)' ;
atom: '[^()\s]+' ;
SPACES: '\s+' (%ignore) ;
