schema = {
  "$schema": "http://json-schema.org/draft-07/schema",
  "$id": "http://example.com/example.json",
  "type": "object",
  "title": "The root schema",
  "description": "The root schema comprises the entire JSON document.",
  "required": [
    "adf"
  ],
  "properties": {
    "adf": {
      "$id": "#/properties/adf",
      "type": "object",
      "title": "The adf schema",
      "description": "An explanation about the purpose of this instance.",
      "default": {},
      "examples": [
        {
          "prospect": {
            "id": [
              {
                "@sequence": "1",
                "@source": "HyundaiMotors",
                "#text": "52376119"
              },
              {
                "@source": "IPAddress",
                "#text": "127.0.0.1"
              },
              {
                "@source": "URL",
                "#text": "www.hyundaiusa.com/buildyourown"
              },
              {
                "@source": "UserAgent",
                "#text": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0."
              },
              {
                "@source": "ProgramID",
                "#text": "75170"
              },
              {
                "@source": "CampaignID",
                "#text": "CMP_5345645644"
              },
              {
                "@source": "ReferrerSite",
                "#text": "www.trilogy.com"
              },
              {
                "@source": "ReferrerType",
                "#text": "Direct"
              },
              {
                "@source": "BrowseHistory",
                "@sequence": "1",
                "#text": "www.hyundaiusa.com"
              },
              {
                "@source": "BrowseHistory",
                "@sequence": "2",
                "#text": "www.hyundaiusa.com/new_santa_fe"
              },
              {
                "@source": "BrowseHistory",
                "@sequence": "3",
                "#text": "www.hyundaiusa.com/buildyourown"
              },
              {
                "@source": "LeadLanguage",
                "#text": "English"
              },
              {
                "@source": "CloudID",
                "#text": "347811007763490181028775335446"
              },
              {
                "@source": "TCPA_Consent",
                "#text": "Yes"
              }
            ],
            "requestdate": "2017-12-08T22:09:37-08:00",
            "vehicle": {
              "@interest": "buy",
              "@status": "new",
              "year": "2017",
              "make": "Hyundai",
              "model": "Santa Fe",
              "transmission": "SE 3.3L 6-Speed Automatic Transmission",
              "trim": "SE",
              "colorcombination": {
                "exteriorcolor": "Monaco White",
                "interiorcolor": "Beige Cloth"
              },
              "price": [
                {
                  "@type": "msrp",
                  "@currency": "USD",
                  "@source": "Hyundai",
                  "#text": "31295"
                },
                {
                  "@type": "quote",
                  "@currency": "USD",
                  "#text": "0"
                }
              ],
              "option": {
                "optionname": "Standard for SE FWD"
              },
              "comments": "Dealer's notes : TRIM INFO: SE SE 3.3L 6-Speed Automatic Transmission\nModel-Package Code :\nQuote Type : Request a Quote\nQuote Responded Date :\nRebate Amount :  0\nRebate Valid Dates :\nRegion : WE"
            },
            "customer": {
              "contact": {
                "name": [
                  {
                    "@part": "first",
                    "#text": "JOHN"
                  },
                  {
                    "@part": "last",
                    "#text": "DOE"
                  }
                ],
                "email": "JOHN.DOE@EMAIL.COM",
                "phone": {
                  "@type": "voice",
                  "@time": "day",
                  "@besttime": "1",
                  "#text": "123-456-7890"
                },
                "address": {
                  "@type": "home",
                  "street": {
                    "@line": "1"
                  },
                  "city": "",
                  "regioncode": "",
                  "postalcode": "85251",
                  "country": "US"
                }
              },
              "timeframe": {
                "description": "0-3 Months"
              },
              "comments": "Customer's notes :\nConsidering Trade-in? : NO\nContact Method :"
            },
            "vendor": {
              "id": {
                "@sequence": "1",
                "@source": "Hyundai Dealer Code",
                "#text": "AZ032"
              }
            },
            "provider": {
              "name": {
                "@part": "full",
                "#text": "HyundaiUSA.com"
              },
              "service": "Hyundai Drive"
            }
          }
        }
      ],
      "required": [
        "prospect"
      ],
      "properties": {
        "prospect": {
          "$id": "#/properties/adf/properties/prospect",
          "type": "object",
          "title": "The prospect schema",
          "description": "An explanation about the purpose of this instance.",
          "default": {},
          "examples": [
            {
              "id": [
                {
                  "@sequence": "1",
                  "@source": "HyundaiMotors",
                  "#text": "52376119"
                },
                {
                  "@source": "IPAddress",
                  "#text": "127.0.0.1"
                },
                {
                  "@source": "URL",
                  "#text": "www.hyundaiusa.com/buildyourown"
                },
                {
                  "@source": "UserAgent",
                  "#text": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0."
                },
                {
                  "@source": "ProgramID",
                  "#text": "75170"
                },
                {
                  "@source": "CampaignID",
                  "#text": "CMP_5345645644"
                },
                {
                  "@source": "ReferrerSite",
                  "#text": "www.trilogy.com"
                },
                {
                  "@source": "ReferrerType",
                  "#text": "Direct"
                },
                {
                  "@source": "BrowseHistory",
                  "@sequence": "1",
                  "#text": "www.hyundaiusa.com"
                },
                {
                  "@source": "BrowseHistory",
                  "@sequence": "2",
                  "#text": "www.hyundaiusa.com/new_santa_fe"
                },
                {
                  "@source": "BrowseHistory",
                  "@sequence": "3",
                  "#text": "www.hyundaiusa.com/buildyourown"
                },
                {
                  "@source": "LeadLanguage",
                  "#text": "English"
                },
                {
                  "@source": "CloudID",
                  "#text": "347811007763490181028775335446"
                },
                {
                  "@source": "TCPA_Consent",
                  "#text": "Yes"
                }
              ],
              "requestdate": "2017-12-08T22:09:37-08:00",
              "vehicle": {
                "@interest": "buy",
                "@status": "new",
                "year": "2017",
                "make": "Hyundai",
                "model": "Santa Fe",
                "transmission": "SE 3.3L 6-Speed Automatic Transmission",
                "trim": "SE",
                "colorcombination": {
                  "exteriorcolor": "Monaco White",
                  "interiorcolor": "Beige Cloth"
                },
                "price": [
                  {
                    "@type": "msrp",
                    "@currency": "USD",
                    "@source": "Hyundai",
                    "#text": "31295"
                  },
                  {
                    "@type": "quote",
                    "@currency": "USD",
                    "#text": "0"
                  }
                ],
                "option": {
                  "optionname": "Standard for SE FWD"
                },
                "comments": "Dealer's notes : TRIM INFO: SE SE 3.3L 6-Speed Automatic Transmission\nModel-Package Code :\nQuote Type : Request a Quote\nQuote Responded Date :\nRebate Amount :  0\nRebate Valid Dates :\nRegion : WE"
              },
              "customer": {
                "contact": {
                  "name": [
                    {
                      "@part": "first",
                      "#text": "JOHN"
                    },
                    {
                      "@part": "last",
                      "#text": "DOE"
                    }
                  ],
                  "email": "JOHN.DOE@EMAIL.COM",
                  "phone": {
                    "@type": "voice",
                    "@time": "day",
                    "@besttime": "1",
                    "#text": "123-456-7890"
                  },
                  "address": {
                    "@type": "home",
                    "street": {
                      "@line": "1"
                    },
                    "city": "",
                    "regioncode": "",
                    "postalcode": "85251",
                    "country": "US"
                  }
                },
                "timeframe": {
                  "description": "0-3 Months"
                },
                "comments": "Customer's notes :\nConsidering Trade-in? : NO\nContact Method :"
              },
              "vendor": {
                "id": {
                  "@sequence": "1",
                  "@source": "Hyundai Dealer Code",
                  "#text": "AZ032"
                }
              },
              "provider": {
                "name": {
                  "@part": "full",
                  "#text": "HyundaiUSA.com"
                },
                "service": "Hyundai Drive"
              }
            }
          ],
          "required": [
            "id",
            "requestdate",
            "vehicle",
            "customer",
            "vendor",
            "provider"
          ],
          "properties": {
            "id": {
              "$id": "#/properties/adf/properties/prospect/properties/id",
              "type": "array",
              "title": "The id schema",
              "description": "An explanation about the purpose of this instance.",
              "default": [],
              "examples": [
                [
                  {
                    "@sequence": "1",
                    "@source": "HyundaiMotors",
                    "#text": "52376119"
                  },
                  {
                    "@source": "IPAddress",
                    "#text": "127.0.0.1"
                  }
                ]
              ],
              "additionalItems": True,
              "items": {
                "$id": "#/properties/adf/properties/prospect/properties/id/items",
                "anyOf": [
                  {
                    "$id": "#/properties/adf/properties/prospect/properties/id/items/anyOf/0",
                    "type": "object",
                    "title": "The first anyOf schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": {},
                    "examples": [
                      {
                        "@sequence": "1",
                        "@source": "HyundaiMotors",
                        "#text": "52376119"
                      }
                    ],
                    "required": [
                    ],
                    "properties": {
                      "@sequence": {
                        "$id": "#/properties/adf/properties/prospect/properties/id/items/anyOf/0/properties/%40sequence",
                        "type": "string",
                        "title": "The @sequence schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": "",
                        "examples": [
                          "1"
                        ]
                      },
                      "@source": {
                        "$id": "#/properties/adf/properties/prospect/properties/id/items/anyOf/0/properties/%40source",
                        "type": "string",
                        "title": "The @source schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": "",
                        "examples": [
                          "HyundaiMotors"
                        ]
                      },
                      "#text": {
                        "$id": "#/properties/adf/properties/prospect/properties/id/items/anyOf/0/properties/%23text",
                        "type": "string",
                        "title": "The #text schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": "",
                        "examples": [
                          "52376119"
                        ]
                      }
                    },
                    
                  },
                  {
                    "$id": "#/properties/adf/properties/prospect/properties/id/items/anyOf/1",
                    "type": "object",
                    "title": "The second anyOf schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": {},
                    "examples": [
                      {
                        "@source": "IPAddress",
                        "#text": "127.0.0.1"
                      }
                    ],
                    "required": [
                    ],
                    "properties": {
                      "@source": {
                        "$id": "#/properties/adf/properties/prospect/properties/id/items/anyOf/1/properties/%40source",
                        "type": "string",
                        "title": "The @source schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": "",
                        "examples": [
                          "IPAddress"
                        ]
                      },
                      "#text": {
                        "$id": "#/properties/adf/properties/prospect/properties/id/items/anyOf/1/properties/%23text",
                        "type": "string",
                        "title": "The #text schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": "",
                        "examples": [
                          "127.0.0.1"
                        ]
                      }
                    },
                    
                  }
                ]
              }
            },
            "requestdate": {
              "$id": "#/properties/adf/properties/prospect/properties/requestdate",
              "type": "string",
              "title": "The requestdate schema",
              "description": "An explanation about the purpose of this instance.",
              "default": "",
              "examples": [
                "2017-12-08T22:09:37-08:00"
              ]
            },
            "vehicle": {
              "$id": "#/properties/adf/properties/prospect/properties/vehicle",
              "type": "object",
              "title": "The vehicle schema",
              "description": "An explanation about the purpose of this instance.",
              "default": {},
              "examples": [
                {
                  "@interest": "buy",
                  "@status": "new",
                  "year": "2017",
                  "make": "Hyundai",
                  "model": "Santa Fe",
                  "transmission": "SE 3.3L 6-Speed Automatic Transmission",
                  "trim": "SE",
                  "colorcombination": {
                    "exteriorcolor": "Monaco White",
                    "interiorcolor": "Beige Cloth"
                  },
                  "price": [
                    {
                      "@type": "msrp",
                      "@currency": "USD",
                      "@source": "Hyundai",
                      "#text": "31295"
                    },
                    {
                      "@type": "quote",
                      "@currency": "USD",
                      "#text": "0"
                    }
                  ],
                  "option": {
                    "optionname": "Standard for SE FWD"
                  },
                  "comments": "Dealer's notes : TRIM INFO: SE SE 3.3L 6-Speed Automatic Transmission\nModel-Package Code :\nQuote Type : Request a Quote\nQuote Responded Date :\nRebate Amount :  0\nRebate Valid Dates :\nRegion : WE"
                }
              ],
              "required": [
                "year",
                "make",
                "model"
              ],
              "properties": {
                "@interest": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/%40interest",
                  "type": "string",
                  "title": "The @interest schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": "",
                  "examples": [
                    "buy"
                  ]
                },
                "@status": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/%40status",
                  "type": "string",
                  "title": "The @status schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": "",
                  "examples": [
                    "new"
                  ]
                },
                "year": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/year",
                  "type": "string",
                  "title": "The year schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": "",
                  "examples": [
                    "2017"
                  ]
                },
                "make": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/make",
                  "type": "string",
                  "title": "The make schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": "",
                  "examples": [
                    "Hyundai"
                  ]
                },
                "model": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/model",
                  "type": "string",
                  "title": "The model schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": "",
                  "examples": [
                    "Santa Fe"
                  ]
                },
                "transmission": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/transmission",
                  "type": "string",
                  "title": "The transmission schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": "",
                  "examples": [
                    "SE 3.3L 6-Speed Automatic Transmission"
                  ]
                },
                "trim": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/trim",
                  "type": "string",
                  "title": "The trim schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": "",
                  "examples": [
                    "SE"
                  ]
                },
                "colorcombination": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/colorcombination",
                  "type": "object",
                  "title": "The colorcombination schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": {},
                  "examples": [
                    {
                      "exteriorcolor": "Monaco White",
                      "interiorcolor": "Beige Cloth"
                    }
                  ],
                  "required": [
                  ],
                  "properties": {
                    "exteriorcolor": {
                      "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/colorcombination/properties/exteriorcolor",
                      "type": "string",
                      "title": "The exteriorcolor schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": "",
                      "examples": [
                        "Monaco White"
                      ]
                    },
                    "interiorcolor": {
                      "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/colorcombination/properties/interiorcolor",
                      "type": "string",
                      "title": "The interiorcolor schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": "",
                      "examples": [
                        "Beige Cloth"
                      ]
                    }
                  }
                },
                "price": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price",
                  "type": "array",
                  "title": "The price schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": [],
                  "examples": [
                    [
                      {
                        "@type": "msrp",
                        "@currency": "USD",
                        "@source": "Hyundai",
                        "#text": "31295"
                      },
                      {
                        "@type": "quote",
                        "@currency": "USD",
                        "#text": "0"
                      }
                    ]
                  ],
                  "additionalItems": True,
                  "items": {
                    "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price/items",
                    "anyOf": [
                      {
                        "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price/items/anyOf/0",
                        "type": "object",
                        "title": "The first anyOf schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": {},
                        "examples": [
                          {
                            "@type": "msrp",
                            "@currency": "USD",
                            "@source": "Hyundai",
                            "#text": "31295"
                          }
                        ],
                        "required": [
                        ],
                        "properties": {
                          "@type": {
                            "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price/items/anyOf/0/properties/%40type",
                            "type": "string",
                            "title": "The @type schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                              "msrp"
                            ]
                          },
                          "@currency": {
                            "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price/items/anyOf/0/properties/%40currency",
                            "type": "string",
                            "title": "The @currency schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                              "USD"
                            ]
                          },
                          "@source": {
                            "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price/items/anyOf/0/properties/%40source",
                            "type": "string",
                            "title": "The @source schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                              "Hyundai"
                            ]
                          },
                          "#text": {
                            "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price/items/anyOf/0/properties/%23text",
                            "type": "string",
                            "title": "The #text schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                              "31295"
                            ]
                          }
                        }
                      },
                      {
                        "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price/items/anyOf/1",
                        "type": "object",
                        "title": "The second anyOf schema",
                        "description": "An explanation about the purpose of this instance.",
                        "default": {},
                        "examples": [
                          {
                            "@type": "quote",
                            "@currency": "USD",
                            "#text": "0"
                          }
                        ],
                        "required": [
                        ],
                        "properties": {
                          "@type": {
                            "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price/items/anyOf/1/properties/%40type",
                            "type": "string",
                            "title": "The @type schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                              "quote"
                            ]
                          },
                          "@currency": {
                            "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price/items/anyOf/1/properties/%40currency",
                            "type": "string",
                            "title": "The @currency schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                              "USD"
                            ]
                          },
                          "#text": {
                            "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/price/items/anyOf/1/properties/%23text",
                            "type": "string",
                            "title": "The #text schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                              "0"
                            ]
                          }
                        }
                      }
                    ]
                  }
                },
                "option": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/option",
                  "type": "object",
                  "title": "The option schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": {},
                  "examples": [
                    {
                      "optionname": "Standard for SE FWD"
                    }
                  ],
                  "required": [
                  ],
                  "properties": {
                    "optionname": {
                      "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/option/properties/optionname",
                      "type": "string",
                      "title": "The optionname schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": "",
                      "examples": [
                        "Standard for SE FWD"
                      ]
                    }
                  }
                },
                "comments": {
                  "$id": "#/properties/adf/properties/prospect/properties/vehicle/properties/comments",
                  "type": "string",
                  "title": "The comments schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": "",
                  "examples": [
                    "Dealer's notes : TRIM INFO: SE SE 3.3L 6-Speed Automatic Transmission\nModel-Package Code :\nQuote Type : Request a Quote\nQuote Responded Date :\nRebate Amount :  0\nRebate Valid Dates :\nRegion : WE"
                  ]
                }
              },
              
            },
            "customer": {
              "$id": "#/properties/adf/properties/prospect/properties/customer",
              "type": "object",
              "title": "The customer schema",
              "description": "An explanation about the purpose of this instance.",
              "default": {},
              "examples": [
                {
                  "contact": {
                    "name": [
                      {
                        "@part": "first",
                        "#text": "JOHN"
                      },
                      {
                        "@part": "last",
                        "#text": "DOE"
                      }
                    ],
                    "email": "JOHN.DOE@EMAIL.COM",
                    "phone": {
                      "@type": "voice",
                      "@time": "day",
                      "@besttime": "1",
                      "#text": "123-456-7890"
                    },
                    "address": {
                      "@type": "home",
                      "street": {
                        "@line": "1"
                      },
                      "city": "",
                      "regioncode": "",
                      "postalcode": "85251",
                      "country": "US"
                    }
                  },
                  "timeframe": {
                    "description": "0-3 Months"
                  },
                  "comments": "Customer's notes :\nConsidering Trade-in? : NO\nContact Method :"
                }
              ],
              "required": [
                "contact"
              ],
              "properties": {
                "contact": {
                  "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact",
                  "type": "object",
                  "title": "The contact schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": {},
                  "examples": [
                    {
                      "name": [
                        {
                          "@part": "first",
                          "#text": "JOHN"
                        },
                        {
                          "@part": "last",
                          "#text": "DOE"
                        }
                      ],
                      "email": "JOHN.DOE@EMAIL.COM",
                      "phone": {
                        "@type": "voice",
                        "@time": "day",
                        "@besttime": "1",
                        "#text": "123-456-7890"
                      },
                      "address": {
                        "@type": "home",
                        "street": {
                          "@line": "1"
                        },
                        "city": "",
                        "regioncode": "",
                        "postalcode": "85251",
                        "country": "US"
                      }
                    }
                  ],
                  "required": [
                    "name",
                    "address"
                  ],
                  "properties": {
                    "name": {
                      "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/name",
                      "type": "array",
                      "title": "The name schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": [],
                      "examples": [
                        [
                          {
                            "@part": "first",
                            "#text": "JOHN"
                          },
                          {
                            "@part": "last",
                            "#text": "DOE"
                          }
                        ]
                      ],
                      "items": {
                        "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/name/items",
                        "anyOf": [
                          {
                            "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/name/items/anyOf/0",
                            "type": "object",
                            "title": "The first anyOf schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": {},
                            "examples": [
                              {
                                "@part": "first",
                                "#text": "JOHN"
                              }
                            ],
                            "required": [
                            ],
                            "properties": {
                              "@part": {
                                "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/name/items/anyOf/0/properties/%40part",
                                "type": "string",
                                "title": "The @part schema",
                                "description": "An explanation about the purpose of this instance.",
                                "default": "",
                                "examples": [
                                  "first"
                                ]
                              },
                              "#text": {
                                "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/name/items/anyOf/0/properties/%23text",
                                "type": "string",
                                "title": "The #text schema",
                                "description": "An explanation about the purpose of this instance.",
                                "default": "",
                                "examples": [
                                  "JOHN"
                                ]
                              }
                            }
                          }
                        ]
                      }
                    },
                    "email": {
                      "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/email",
                      "type": "string",
                      "title": "The email schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": "",
                      "examples": [
                        "JOHN.DOE@EMAIL.COM"
                      ]
                    },
                    "phone": {
                      "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/phone",
                      "type": "object",
                      "title": "The phone schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": {},
                      "examples": [
                        {
                          "@type": "voice",
                          "@time": "day",
                          "@besttime": "1",
                          "#text": "123-456-7890"
                        }
                      ],
                      "required": [
                      ],
                      "properties": {
                        "@type": {
                          "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/phone/properties/%40type",
                          "type": "string",
                          "title": "The @type schema",
                          "description": "An explanation about the purpose of this instance.",
                          "default": "",
                          "examples": [
                            "voice"
                          ]
                        },
                        "@time": {
                          "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/phone/properties/%40time",
                          "type": "string",
                          "title": "The @time schema",
                          "description": "An explanation about the purpose of this instance.",
                          "default": "",
                          "examples": [
                            "day"
                          ]
                        },
                        "@besttime": {
                          "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/phone/properties/%40besttime",
                          "type": "string",
                          "title": "The @besttime schema",
                          "description": "An explanation about the purpose of this instance.",
                          "default": "",
                          "examples": [
                            "1"
                          ]
                        },
                        "#text": {
                          "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/phone/properties/%23text",
                          "type": "string",
                          "title": "The #text schema",
                          "description": "An explanation about the purpose of this instance.",
                          "default": "",
                          "examples": [
                            "123-456-7890"
                          ]
                        }
                      },
                      
                    },
                    "address": {
                      "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/address",
                      "type": "object",
                      "title": "The address schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": {},
                      "examples": [
                        {
                          "@type": "home",
                          "street": {
                            "@line": "1"
                          },
                          "city": "",
                          "regioncode": "",
                          "postalcode": "85251",
                          "country": "US"
                        }
                      ],
                      "required": [
                        "postalcode"
                      ],
                      "properties": {
                        "@type": {
                          "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/address/properties/%40type",
                          "type": "string",
                          "title": "The @type schema",
                          "description": "An explanation about the purpose of this instance.",
                          "default": "",
                          "examples": [
                            "home"
                          ]
                        },
                        "street": {
                          "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/address/properties/street",
                          "type": "object",
                          "title": "The street schema",
                          "description": "An explanation about the purpose of this instance.",
                          "default": {},
                          "examples": [
                            {
                              "@line": "1"
                            }
                          ],
                          "required": [
                          ],
                          "properties": {
                            "@line": {
                              "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/address/properties/street/properties/%40line",
                              "type": "string",
                              "title": "The @line schema",
                              "description": "An explanation about the purpose of this instance.",
                              "default": "",
                              "examples": [
                                "1"
                              ]
                            }
                          }
                        },
                        "city": {
                          "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/address/properties/city",
                          "type": ["string"],
                          "title": "The city schema",
                          "description": "An explanation about the purpose of this instance.",
                          "default": "",
                          "examples": [
                            ""
                          ]
                        },
                        "regioncode": {
                          "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/address/properties/regioncode",
                          "type": "string",
                          "title": "The regioncode schema",
                          "description": "An explanation about the purpose of this instance.",
                          "default": "",
                          "examples": [
                            ""
                          ]
                        },
                        "postalcode": {
                          "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/address/properties/postalcode",
                          "type": "string",
                          "title": "The postalcode schema",
                          "description": "An explanation about the purpose of this instance.",
                          "default": "",
                          "examples": [
                            "85251"
                          ]
                        },
                        "country": {
                          "$id": "#/properties/adf/properties/prospect/properties/customer/properties/contact/properties/address/properties/country",
                          "type": "string",
                          "title": "The country schema",
                          "description": "An explanation about the purpose of this instance.",
                          "default": "",
                          "examples": [
                            "US"
                          ]
                        }
                      },
                      
                    }
                  }
                },
                "timeframe": {
                  "$id": "#/properties/adf/properties/prospect/properties/customer/properties/timeframe",
                  "type": "object",
                  "title": "The timeframe schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": {},
                  "examples": [
                    {
                      "description": "0-3 Months"
                    }
                  ],
                  "required": [
                  ],
                  "properties": {
                    "description": {
                      "$id": "#/properties/adf/properties/prospect/properties/customer/properties/timeframe/properties/description",
                      "type": "string",
                      "title": "The description schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": "",
                      "examples": [
                        "0-3 Months"
                      ]
                    }
                  }
                },
                "comments": {
                  "$id": "#/properties/adf/properties/prospect/properties/customer/properties/comments",
                  "type": "string",
                  "title": "The comments schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": "",
                  "examples": [
                    "Customer's notes :\nConsidering Trade-in? : NO\nContact Method :"
                  ]
                }
              },
              
            },
            "vendor": {
              "$id": "#/properties/adf/properties/prospect/properties/vendor",
              "type": "object",
              "title": "The vendor schema",
              "description": "An explanation about the purpose of this instance.",
              "default": {},
              "examples": [
                {
                  "id": {
                    "@sequence": "1",
                    "@source": "Hyundai Dealer Code",
                    "#text": "AZ032"
                  }
                }
              ],
              "required": [
                "id"
              ],
              "properties": {
                "id": {
                  "$id": "#/properties/adf/properties/prospect/properties/vendor/properties/id",
                  "type": "object",
                  "title": "The id schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": {},
                  "examples": [
                    {
                      "@sequence": "1",
                      "@source": "Hyundai Dealer Code",
                      "#text": "AZ032"
                    }
                  ],
                  "required": [
                  ],
                  "properties": {
                    "@sequence": {
                      "$id": "#/properties/adf/properties/prospect/properties/vendor/properties/id/properties/%40sequence",
                      "type": "string",
                      "title": "The @sequence schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": "",
                      "examples": [
                        "1"
                      ]
                    },
                    "@source": {
                      "$id": "#/properties/adf/properties/prospect/properties/vendor/properties/id/properties/%40source",
                      "type": "string",
                      "title": "The @source schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": "",
                      "examples": [
                        "Hyundai Dealer Code"
                      ]
                    },
                    "#text": {
                      "$id": "#/properties/adf/properties/prospect/properties/vendor/properties/id/properties/%23text",
                      "type": "string",
                      "title": "The #text schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": "",
                      "examples": [
                        "AZ032"
                      ]
                    }
                  }
                }
              },
              
            },
            "provider": {
              "$id": "#/properties/adf/properties/prospect/properties/provider",
              "type": "object",
              "title": "The provider schema",
              "description": "An explanation about the purpose of this instance.",
              "default": {},
              "examples": [
                {
                  "name": {
                    "@part": "full",
                    "#text": "HyundaiUSA.com"
                  },
                  "service": "Hyundai Drive"
                }
              ],
              "required": [
                "name",
                "service"
              ],
              "properties": {
                "name": {
                  "$id": "#/properties/adf/properties/prospect/properties/provider/properties/name",
                  "type": "object",
                  "title": "The name schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": {},
                  "examples": [
                    {
                      "@part": "full",
                      "#text": "HyundaiUSA.com"
                    }
                  ],
                  "required": [
                  ],
                  "properties": {
                    "@part": {
                      "$id": "#/properties/adf/properties/prospect/properties/provider/properties/name/properties/%40part",
                      "type": "string",
                      "title": "The @part schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": "",
                      "examples": [
                        "full"
                      ]
                    },
                    "#text": {
                      "$id": "#/properties/adf/properties/prospect/properties/provider/properties/name/properties/%23text",
                      "type": "string",
                      "title": "The #text schema",
                      "description": "An explanation about the purpose of this instance.",
                      "default": "",
                      "examples": [
                        "HyundaiUSA.com"
                      ]
                    }
                  }
                },
                "service": {
                  "$id": "#/properties/adf/properties/prospect/properties/provider/properties/service",
                  "type": "string",
                  "title": "The service schema",
                  "description": "An explanation about the purpose of this instance.",
                  "default": "",
                  "examples": [
                    "Hyundai Drive"
                  ]
                }
              },
              
            }
          },
          
        }
      },
      
    }
  },
  
}