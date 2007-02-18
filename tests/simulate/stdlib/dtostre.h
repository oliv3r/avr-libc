/* Header+source file to test the dtostre() function.
   $Id$
 */

#ifndef	PATTERN_SIZE
# define PATTERN_SIZE	15
#endif

struct dtostre_s {
    union {
	long lo;
	float fl;
    };
    unsigned char prec;
    unsigned char flags;
    char pattern[PATTERN_SIZE];
};

#ifndef	__AVR__

# include <stdio.h>
# include <string.h>

# define DTOSTR_ALWAYS_SIGN 0x01	/* put '+' or ' ' for positives */
# define DTOSTR_PLUS_SIGN   0x02	/* put '+' rather than ' ' */
# define DTOSTR_UPPERCASE   0x04	/* put 'E' rather 'e' */

/* This function is intended for run of test cases on the host computer.
 */
char * dtostre (double val, char *s, unsigned char prec, unsigned char flags)
{
    char fmt[8];
    char sign[2];
    char e;
    
    if (prec > 7) prec = 7;
    
    strcpy(sign, "");
    if (flags & DTOSTR_ALWAYS_SIGN)
	strcpy(sign, " ");
    if (flags & DTOSTR_PLUS_SIGN)
	strcpy(sign, "+");

    e = (flags & DTOSTR_UPPERCASE) ? 'E' : 'e';

    sprintf(fmt, "%%%s.%d%c", sign, prec, e);
    sprintf(s, fmt, val);
    return s;
}
#endif	/* !__AVR__ */

#define	PZLEN	5	/* protected zone length	*/

void run_dtostre (const struct dtostre_s *pt, int testno)
{
    union {
	long lo;
	float fl;
    } val;
    unsigned char prec, flags;
    static char s[2*PZLEN + sizeof(pt->pattern)];
    char c, *ps;
    void *pv;
    
    memset(s, testno, sizeof(s));

#ifdef	__AVR__
    val.lo = pgm_read_dword (& pt->lo);
    prec   = pgm_read_byte (& pt->prec);
    flags  = pgm_read_byte (& pt->flags);
#else
    val.lo = pt->lo;
    prec   = pt->prec;
    flags  = pt->flags;
#endif
    ps = dtostre (val.fl, s + PZLEN, prec, flags);

    if (ps != s + PZLEN)
	exit (testno + 0x1000);
    for (ps = s; ps != s + PZLEN; ps++) {
	if ((unsigned char)*ps != (testno & 0377))
	    exit (testno + 0x2000);
    }

    pv = & pt->pattern;
#ifdef	__AVR__
    do {
	c = pgm_read_byte(pv++);
	if (*ps++ != c) {
	    exit (testno + 0x3000);
	}
    } while (c);
#else
    do {
	c = *(char *)(pv++);
	if (*ps++ != c) {
	    printf ("*** testno= %d:  must= %s  was= %s\n",
		testno, pt->pattern, s + PZLEN);
	    exit (testno + 0x3000);
	}
    } while (c);
#endif

    for (; ps != s + sizeof(s); ps++) {
	if ((unsigned char)*ps != (testno & 0377))
	    exit (testno + 0x4000);
    }
}