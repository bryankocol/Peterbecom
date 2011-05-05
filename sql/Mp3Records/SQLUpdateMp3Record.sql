<params>id
am_URL
am_ImageUrlLarge
am_ImageUrlMedium
am_ImageUrlSmall
am_Tracks
am_OurPrice
am_ProductName</params>

UPDATE mp3records

SET
<dtml-if "am_URL!=_.None">
 am_url = <dtml-sqlvar am_URL type="string">,
</dtml-if>

<dtml-if "am_ImageUrlLarge!=_.None">
 am_imageurllarge = <dtml-sqlvar am_ImageUrlLarge type="string">,
</dtml-if>

<dtml-if "am_ImageUrlMedium!=_.None">
 am_imageurlmedium = <dtml-sqlvar am_ImageUrlMedium type="string">,
</dtml-if>

<dtml-if "am_ImageUrlSmall!=_.None">
 am_imageurlsmall = <dtml-sqlvar am_ImageUrlSmall type="string">,
</dtml-if>

<dtml-if "am_Tracks!=_.None">
 am_tracks = <dtml-sqlvar am_Tracks type="string">,
</dtml-if>

<dtml-if "am_OurPrice!=_.None">
 am_ourprice = <dtml-sqlvar am_OurPrice type="string">,
</dtml-if>

<dtml-if "am_ProductName!=_.None">
 am_productname = <dtml-sqlvar am_ProductName type="string">,
</dtml-if>

 time_stamp = now()

WHERE
 id = <dtml-sqlvar id type="int">
