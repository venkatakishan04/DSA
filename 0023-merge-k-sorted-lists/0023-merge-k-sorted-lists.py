# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        l=[]
        for i in lists:
            while i:
                l.append(i.val)
                i=i.next
        l.sort()
        if(len(l)==0):
            return None
        head=ListNode(l[0])
        ptr=head
        for i in range(1,len(l)):
            ptr.next=ListNode(l[i])
            ptr=ptr.next
        return head