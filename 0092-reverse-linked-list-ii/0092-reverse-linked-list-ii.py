# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        if(left-right==0):
            return head
        ltemp=None
        rtemp=head
        l=1
        lptr=head
        rptr=head
        while(l<left):
            ltemp=lptr
            lptr=lptr.next
            l+=1
        r=1
        while(r<right):
            rptr=rptr.next
            r+=1
        rtemp=rptr.next
        prev=rtemp
        curr=lptr
        while(curr!=rtemp):
            nxt=curr.next
            curr.next=prev
            prev=curr
            curr=nxt
        if(ltemp):
            ltemp.next=prev
        else:
            head=prev
        return head
