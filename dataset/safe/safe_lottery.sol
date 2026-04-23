// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeLottery {
    mapping(address => uint256) public tickets;
    function buyTicket() public payable {
        require(msg.value == 0.01 ether, "Wrong amount");
        tickets[msg.sender] += 1;
    }
}