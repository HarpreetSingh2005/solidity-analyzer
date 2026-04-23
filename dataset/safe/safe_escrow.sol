// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeEscrow {
    address public buyer;
    address public seller;
    uint256 public amount;
    bool public released;

    constructor(address _seller) payable {
        buyer = msg.sender;
        seller = _seller;
        amount = msg.value;
    }

    function release() external {
        require(msg.sender == buyer, "Only buyer");
        require(!released, "Already released");
        released = true;
        payable(seller).transfer(amount);
    }
}