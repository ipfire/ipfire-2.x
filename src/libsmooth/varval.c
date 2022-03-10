/* SmoothWall libsmooth.
 *
 * This program is distributed under the terms of the GNU General Public
 * Licence.  See the file COPYING for details.
 *
 * (c) Lawrence Manning, 2001
 * Contains functions for manipulation files full of VAR=VAL pairs.
 *
 * 2003-07-27 Robert Kerr - Added cooperative file locking to prevent any
 * clashes between setuid programs reading configuration and cgi scripts
 * trying to write it
 *
 */

#include "libsmooth.h"

/* Sets up the list.  First entry is a dummy one to avoid having to special
 * case empty lists. */
struct keyvalue *initkeyvalues(void)
{
 	struct keyvalue *head = malloc(sizeof(struct keyvalue));

	strcpy(head->key, "KEY");
	strcpy(head->value, "VALUE");
	head->next = NULL;

	return head;
}

/* Splats all the entries in a list. */
void freekeyvalues(struct keyvalue *head)
{
	struct keyvalue *cur = head->next;
	struct keyvalue *next;

	while (cur)
	{
		next = cur->next;
		free(cur);
		cur = next;
	}
}

/* Reads from a file into a new list.  Uses appendkeyvalue to add entries.
 * Will bomb out on a error (eg bad format line). */
int readkeyvalues(struct keyvalue *head, char *filename)
{
 	FILE *file;
	char buffer[STRING_SIZE];
	char *temp;
	char *key, *value;

	if (!(file = fopen(filename, "r")))
		return 0;

	if (flock(fileno(file), LOCK_SH))
	{
		fclose(file);
		return 0;
	}

	while (fgets(buffer, STRING_SIZE, file))
	{
		temp = buffer;
		while (*temp)
		{
			if (*temp =='\n') *temp = '\0';
			temp++;
		}
		if (!strlen(buffer))
			continue;
		if (!(temp = strchr(buffer, '=')))
		{
			flock(fileno(file), LOCK_UN);
			fclose(file);
			return 0;
		}
		*temp = '\0';
		key = buffer; value = temp + 1;
		/* See if string is quoted.  If so, skip first quote, and
		 * nuke the one at the end. */
		if (value[0] == '\'')
		{
			value++;
			if ((temp = strrchr(value, '\'')))
				*temp = '\0';
			else
			{
				flock(fileno(file), LOCK_UN);
				fclose(file);
				return 0;
			}
		}
		if (strlen(key))
			appendkeyvalue(head, key, value);
	}

	flock(fileno(file), LOCK_UN);
	fclose(file);

	return 1;
}

/* Writes out a list to a file.  Easy. */
int writekeyvalues(struct keyvalue *head, char *filename)
{
	FILE *file;
	struct keyvalue *cur = head->next;

	if (!(file = fopen(filename, "w")))
		return 0;

	if (flock(fileno(file), LOCK_EX))
	{
		fclose(file);
		return 0;
	}


	while (cur)
	{
		/* No space in value?  If there is, we need to quote the value
		 * so the shell can read it. */
		if (!strchr(cur->value, ' '))
			fprintf(file, "%s=%s\n", cur->key, cur->value);
		else
			fprintf(file, "%s=\'%s\'\n", cur->key, cur->value);
		cur = cur->next;
	}
	flock(fileno(file), LOCK_UN);
	fclose(file);

	return 1;
}

/* Finds a key and copies the value back.  value must be at least STRING_SIZE
 * long. Would be nice to have a func that just returns a pointer to the value?
 */
int findkey(struct keyvalue *head, char *key, char *value)
{
	struct keyvalue *cur = head->next;

	while (cur)
	{
		if (strcmp(key, cur->key) == 0)
		{
			strncpy(value, cur->value, STRING_SIZE);
			value[STRING_SIZE-1] = '\0';
			return 1;
		}
		cur = cur->next;
	}

	return 0;
}

/* Appends a entry.  Not very efficent because it rescans the list looking
 * for the end.  Maybe fix this later. */
void appendkeyvalue(struct keyvalue *head, char *key, char *value)
{
	struct keyvalue *new = malloc(sizeof(struct keyvalue));
	struct keyvalue *cur = head->next;
	struct keyvalue *tail = head;

	strncpy(new->key, key, STRING_SIZE);
	strncpy(new->value, value, STRING_SIZE);
	new->key[STRING_SIZE-1] = '\0';
	new->value[STRING_SIZE-1] = '\0';
	new->next = NULL;

	while (cur)
	{
		tail = cur;
		cur = cur->next;
	}
	tail->next = new;
}

/* Otherwrites a key with a new value, or if it dosn't exist, appends it
 * on the end. */
void replacekeyvalue(struct keyvalue *head, char *key, char *value)
{
	struct keyvalue *cur = head->next;

	while (cur)
	{
		if (strcmp(cur->key, key) == 0)
		{
			strncpy(cur->value, value, STRING_SIZE);
			cur->value[STRING_SIZE-1] = '\0';
			return;
		}
		cur = cur->next;
	}

	appendkeyvalue(head, key, value);
}
