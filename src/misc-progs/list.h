/* list.h by Jan Bobrowski. Inspired by list.h from Linux */

#ifndef LIST_H
#define LIST_H

typedef struct list {
	struct list *next, *prev;
} list_t;

static inline void list_link(struct list *a, struct list *b)
{
	a->next = b;
	b->prev = a;
}

static inline void list_add(struct list *head, struct list *item)
{
	struct list *first = head->next;
	list_link(head, item);
	list_link(item, first);
}

static inline void list_add_end(struct list *head, struct list *item)
{
	struct list *last = head->prev;
	list_link(item, head);
	list_link(last, item);
}

static inline list_t *list_del(struct list *item)
{
	struct list *prev = item->prev, *next = item->next;
	list_link(prev, next);
	return next;
}

static inline void list_init(struct list *head)
{
	list_link(head, head);
}

/* delete item from one list and add it to another */
static inline void list_del_add(list_t *head, list_t *item)
{
	list_t *prev = item->prev, *next = item->next;
	list_link(prev, next);
	next = head->next;
	list_link(head, item);
	list_link(item, next);
}

/*static inline list_check(list_t *l)
{
	list_t *a = l;
	list_t *b;
	do {
		b = a->next;
		assert(b->prev == a);
		if(a==l) break;
		a = b;
	} while(1);
}*/

static inline void list_del_add_end(list_t *head, list_t *item)
{
	list_t *prev = item->prev, *next = item->next;
	list_link(prev, next);
	prev = head->prev;
	list_link(item, head);
	item->prev = prev;
	prev->next = item;
}

static inline void list_del_init(struct list *item)
{
	struct list *prev = item->prev, *next = item->next;
	list_link(item, item);
	list_link(prev, next);
}

static inline void list_join(struct list *a, struct list *b)
{
	list_t *ae = a->prev;
	list_t *be = b->prev;
	b->prev = ae;
	a->prev = be;
	ae->next = b;
	be->next = a;
}

static inline int list_empty(struct list *head)
{
	return head->next == head;
}

#define LIST(L) struct list L = {&L, &L}

#define list_entry(L, T, M) ((T*)((char*)(L) - (long)(&((T*)0)->M)))
#define list_item(L, T, M) ((T*)((char*)(L) - (long)(&((T*)0)->M)))

#define list_first(H, T, M) list_item((H)->next, T, M)
#define list_last(H, T, M) list_item((H)->prev, T, M)
#define list_next(O, M) list_item((O)->M.next, typeof(*(O)), M)

/* remove first element and return it */
static inline struct list *list_get(struct list *head)
{
	struct list *item = head->next;
	struct list *next = item->next;
	list_link(head, next);
	return item;
}

/* remove first element, initialize and return it */
static inline struct list *list_get_init(struct list *head)
{
	struct list *item = head->next;
	struct list *next = item->next;
	list_link(item, item);
	list_link(head, next);
	return item;
}

#define list_get_entry(H, T, M) list_item(list_get((H)), T, M)
#define list_get_init_entry(H, T, M) list_item(list_get_init((H)), T, M)
#define list_get_item(H, T, M) list_item(list_get((H)), T, M)
#define list_get_init_item(H, T, M) list_item(list_get_init((H)), T, M)

#endif
