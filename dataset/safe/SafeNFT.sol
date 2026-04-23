// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe ERC721 implementation with standard ownership checks.
contract SafeNFT {
    string public name = "Safe NFT";
    string public symbol = "SNFT";
    uint256 public nextTokenId;

    mapping(uint256 => address) private _owners;
    mapping(address => uint256) private _balances;
    mapping(uint256 => address) private _tokenApprovals;
    mapping(address => mapping(address => bool)) private _operatorApprovals;

    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);

    function balanceOf(address owner) public view returns (uint256) {
        require(owner != address(0), "Zero address query");
        return _balances[owner];
    }

    function ownerOf(uint256 tokenId) public view returns (address) {
        address owner = _owners[tokenId];
        require(owner != address(0), "Token does not exist");
        return owner;
    }

    function mint(address to) external {
        require(to != address(0), "Mint to zero address");
        
        uint256 tokenId = nextTokenId++;
        _balances[to] += 1;
        _owners[tokenId] = to;

        emit Transfer(address(0), to, tokenId);
    }

    function transferFrom(address from, address to, uint256 tokenId) public {
        require(ownerOf(tokenId) == from, "Not token owner");
        require(to != address(0), "Transfer to zero address");
        require(msg.sender == from || _operatorApprovals[from][msg.sender] || _tokenApprovals[tokenId] == msg.sender, "Not authorized");

        _balances[from] -= 1;
        _balances[to] += 1;
        _owners[tokenId] = to;
        delete _tokenApprovals[tokenId];

        emit Transfer(from, to, tokenId);
    }
}