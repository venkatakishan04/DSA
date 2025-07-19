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
                heapq.heappush(l,i.val)
                i=i.next
        print(l)
        if(len(l)==0):
            return None
        head=ListNode()
        ptr=head
        while l:
            n=heapq.heappop(l)
            ptr.next=ListNode(n)
            ptr=ptr.next
        print(l)
        return head.next